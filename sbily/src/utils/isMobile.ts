declare global {
  interface Window {
    opera: string;
    MSStream: unknown;
  }
}

export function isMobile(): boolean {
  const userAgent: string =
    // eslint-disable-next-line node/no-unsupported-features/node-builtins
    navigator?.userAgent ?? navigator?.vendor ?? window?.opera ?? "";

  const ANDROID_PATTERN = /android/i;
  const IOS_PATTERN = /ip(?:ad|hone|od)/i;
  const IE_MOBILE_PATTERN = /iemobile/i;
  const MOBILE_PATTERN = /mobile/i;

  return (
    ANDROID_PATTERN.test(userAgent) ||
    (IOS_PATTERN.test(userAgent) && !window.MSStream) ||
    IE_MOBILE_PATTERN.test(userAgent) ||
    MOBILE_PATTERN.test(userAgent)
  );
}
