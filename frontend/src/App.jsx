import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import About from "./pages/About.jsx";
import Alerts from "./pages/Alerts.jsx";
import AnalysisHistory from "./pages/AnalysisHistory.jsx";
import AnimalDetail from "./pages/AnimalDetail.jsx";
import Animals from "./pages/Animals.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ImageAnalysis from "./pages/ImageAnalysis.jsx";
import LiveCamera from "./pages/LiveCamera.jsx";
import VideoAnalysis from "./pages/VideoAnalysis.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze/image" element={<ImageAnalysis />} />
        <Route path="/analyze/video" element={<VideoAnalysis />} />
        <Route path="/live" element={<LiveCamera />} />
        <Route path="/animals" element={<Animals />} />
        <Route path="/animals/:animalId" element={<AnimalDetail />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/history" element={<AnalysisHistory />} />
        <Route path="/about" element={<About />} />
      </Route>
    </Routes>
  );
}
