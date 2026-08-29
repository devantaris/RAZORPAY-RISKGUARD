import { AssessForm } from '@/components/AssessForm';
import { LiveFeed } from '@/components/LiveFeed';
import { ThresholdSlider } from '@/components/ThresholdSlider';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">RG</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-900">Razorpay RiskGuard</h1>
              <p className="text-xs text-gray-500">AI Risk Operations Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              V1-V4 Pipeline Ready
            </span>
            <span>Dempster-Shafer Fusion</span>
            <span>100% DECLINE Precision</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-12 gap-6">
        {/* Left: Live API Tester */}
        <section className="col-span-5 bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Transaction Assessor</h2>
          <AssessForm />
        </section>

        {/* Right: Live Feed */}
        <section className="col-span-7 bg-white rounded-2xl border border-gray-200 p-5 shadow-sm flex flex-col" style={{ height: '70vh' }}>
          <h2 className="font-semibold text-gray-900 mb-4">Live Transaction Feed</h2>
          <LiveFeed />
        </section>

        {/* Bottom: Threshold Controls */}
        <section className="col-span-4 bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Threshold Bandit — Jewelry</h2>
          <ThresholdSlider merchantId="merch_jewelry_001" />
        </section>

        <section className="col-span-4 bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Threshold Bandit — Food</h2>
          <ThresholdSlider merchantId="merch_food_001" />
        </section>

        <section className="col-span-4 bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Threshold Bandit — Travel</h2>
          <ThresholdSlider merchantId="merch_travel_001" />
        </section>
      </main>
    </div>
  );
}
