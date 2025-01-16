declare global {
  interface Window {
    opera: string;
    MSStream: any;
  }
}

export function isMobile() {
  // eslint-disable-next-line node/no-unsupported-features/node-builtins
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;

  if (/android/i.test(userAgent)) {
    return true;
  }
  if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
    return true;
  }

  return false;
}
