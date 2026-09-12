import Header from "./components/layout/Header.tsx";
import SupportAnalyzer from "./components/support/SupportAnalyzer.tsx";

function App() {
  return (
    <div className="min-h-screen bg-[#fafafa]">
      <Header />
      <main>
        <SupportAnalyzer />
      </main>
    </div>
  );
}

export default App;
