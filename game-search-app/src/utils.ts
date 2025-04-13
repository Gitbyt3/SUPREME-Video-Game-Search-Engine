export const viewTransition = (callback: () => void, defer: Boolean | number = false) => {
  if (defer) {
    if (defer === true) defer = 16;
    const oriCallback = callback;
    callback = () => {
      oriCallback();
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(true);
        }, defer as number);
      });
    }
  }
  if ('startViewTransition' in document) {
    (document.startViewTransition as any)(callback);
  } else {
    callback();
  }
};