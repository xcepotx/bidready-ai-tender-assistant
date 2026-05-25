export default function ActorSelector({ actorName, setActorName }) {
  const actors = [
    "bid_manager",
    "solution_architect",
    "commercial_team",
    "security_compliance_team",
    "delivery_manager",
    "legal_team",
    "resource_manager",
  ];

  return (
    <div className="actorSelector">
      <span>Acting as</span>
      <select value={actorName} onChange={(e) => setActorName(e.target.value)}>
        {actors.map((actor) => (
          <option key={actor} value={actor}>
            {actor}
          </option>
        ))}
      </select>
    </div>
  );
}
