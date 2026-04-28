/**
 * LeetCode client layer: global (leetcode.com) and China (leetcode.cn).
 * Credentials from env: LEETCODE_SESSION, LEETCODE_CSRF, LEETCODE_CN_SESSION, LEETCODE_CN_CSRF.
 */
import { LeetCode, LeetCodeCN } from "leetcode-query";
export type Site = "global" | "china";
export interface ClientPair {
    client: LeetCode | LeetCodeCN;
    site: Site;
    hasAuth: boolean;
}
declare const AUTH_MSG = "Authentication required. Set LEETCODE_SESSION and LEETCODE_CSRF for global, or LEETCODE_CN_SESSION and LEETCODE_CN_CSRF for China.";
export declare function getClient(site: Site): ClientPair;
export declare function requireAuth(site: Site): void;
export { AUTH_MSG };
