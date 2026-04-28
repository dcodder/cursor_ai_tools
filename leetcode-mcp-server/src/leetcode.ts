/**
 * LeetCode client layer: global (leetcode.com) and China (leetcode.cn).
 * Credentials from env: LEETCODE_SESSION, LEETCODE_CSRF, LEETCODE_CN_SESSION, LEETCODE_CN_CSRF.
 */

import { Credential, LeetCode, LeetCodeCN } from "leetcode-query";

export type Site = "global" | "china";

export interface ClientPair {
  client: LeetCode | LeetCodeCN;
  site: Site;
  hasAuth: boolean;
}

const AUTH_MSG =
  "Authentication required. Set LEETCODE_SESSION and LEETCODE_CSRF for global, or LEETCODE_CN_SESSION and LEETCODE_CN_CSRF for China.";

function buildGlobalCredential(): Credential | null {
  const session = process.env.LEETCODE_SESSION?.trim();
  const csrf = process.env.LEETCODE_CSRF?.trim();
  if (!session) return null;
  return new Credential({ session, csrf: csrf || undefined });
}

function buildCNCredential(): Credential | null {
  const session = process.env.LEETCODE_CN_SESSION?.trim();
  const csrf = process.env.LEETCODE_CN_CSRF?.trim();
  if (!session) return null;
  return new Credential({ session, csrf: csrf || undefined });
}

let globalClient: LeetCode | null = null;
let globalAuth: boolean = false;
let cnClient: LeetCodeCN | null = null;
let cnAuth: boolean = false;

function getGlobalClient(): { client: LeetCode; hasAuth: boolean } {
  if (!globalClient) {
    const cred = buildGlobalCredential();
    globalAuth = !!cred;
    globalClient = new LeetCode(cred);
  }
  return { client: globalClient, hasAuth: globalAuth };
}

function getCNClient(): { client: LeetCodeCN; hasAuth: boolean } {
  if (!cnClient) {
    const cred = buildCNCredential();
    cnAuth = !!cred;
    cnClient = new LeetCodeCN(cred);
  }
  return { client: cnClient, hasAuth: cnAuth };
}

export function getClient(site: Site): ClientPair {
  if (site === "china") {
    const { client, hasAuth } = getCNClient();
    return { client, site: "china", hasAuth };
  }
  const { client, hasAuth } = getGlobalClient();
  return { client, site: "global", hasAuth };
}

export function requireAuth(site: Site): void {
  const { hasAuth } = getClient(site);
  if (!hasAuth) throw new Error(AUTH_MSG);
}

export { AUTH_MSG };
