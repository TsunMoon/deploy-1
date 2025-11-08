import { useEffect, useRef } from 'react';

export function useAutoScroll(dependencies = []) {
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'end'
    });
  }, [dependencies]);

  return scrollRef;
}