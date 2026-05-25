import { useEffect, useState } from "react";

const ACTOR_STORAGE_KEY = "bra_actor";
const DEFAULT_ACTOR_NAME = "bid_manager";

export function useActorName(defaultActorName = DEFAULT_ACTOR_NAME) {
  const [actorName, setActorName] = useState(() => {
    return window.localStorage.getItem(ACTOR_STORAGE_KEY) || defaultActorName;
  });

  useEffect(() => {
    window.localStorage.setItem(ACTOR_STORAGE_KEY, actorName);
  }, [actorName]);

  return [actorName, setActorName];
}
