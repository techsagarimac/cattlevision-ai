export default function About() {
  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>About this project</h1>
          <p className="lede">College major project: AI-based cattle health and welfare monitoring using computer vision.</p>
        </div>
      </header>
      <section className="card">
        <h3>Objective</h3>
        <p>
          CattleVision AI helps a student or farm observer review cattle images and videos for potentially unusual
          movement or posture. It is an engineering demonstration, not a veterinary diagnostic system.
        </p>
      </section>
      <section className="card">
        <h3>How it works</h3>
        <ol>
          <li>YOLO detects cattle (COCO <code>cow</code> class, or a custom cattle model).</li>
          <li>A simple tracker assigns Cow #01, Cow #02, … across video frames.</li>
          <li>Rule-based logic estimates standing, walking, resting, or low activity.</li>
          <li>An experimental risk score (0–100) flags records that may need human inspection.</li>
        </ol>
      </section>
      <section className="card">
        <h3>Language used in the product</h3>
        <ul>
          <li>Possible Health Concern</li>
          <li>Abnormal Activity Detected</li>
          <li>Veterinary Inspection Recommended</li>
        </ul>
        <p>The system never claims a disease name or a confirmed diagnosis.</p>
      </section>
      <section className="card">
        <h3>Limitations</h3>
        <ul>
          <li>COCO cows are not the same as a farm-specific cattle dataset.</li>
          <li>Tracking can swap IDs when animals overlap.</li>
          <li>Limping and posture checks are visual heuristics only.</li>
          <li>A single photograph cannot measure activity over time.</li>
        </ul>
      </section>
    </div>
  );
}
