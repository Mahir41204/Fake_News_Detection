import MisinformationChecker from "../../components/MisinformationChecker";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-800">🔍 MisinfoDetector</h1>
            </div>
            <div className="flex items-center space-x-6">
              <a href="/" className="text-gray-600 hover:text-gray-800 font-medium">
                Home
              </a>
              <a href="/api-pricing" className="text-gray-600 hover:text-gray-800 font-medium">
                Pricing
              </a>
              <a href="/docs" className="text-gray-600 hover:text-gray-800 font-medium">
                API Docs
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className={styles.main}>
        <MisinformationChecker />
      </main>
    </div>
  );
}
