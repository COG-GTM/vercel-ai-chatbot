"use client";

import cx from "classnames";

const PlaneIcon = ({ size = 24 }: { size?: number }) => (
  <svg
    fill="none"
    height={size}
    viewBox="0 0 24 24"
    width={size}
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z" />
  </svg>
);

const SavingsIcon = ({ size = 16 }: { size?: number }) => (
  <svg
    fill="none"
    height={size}
    viewBox="0 0 24 24"
    width={size}
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </svg>
);

interface FlightResult {
  id: string;
  airline: string;
  price: string;
  priceNumeric: number;
  savings: string | null;
  savingsPercent?: number;
  departureTime: string;
  arrivalTime: string;
  duration: string;
  stops: string;
  foundIn: string;
}

interface FlightSearchSummary {
  totalResults: number;
  countriesSearched: string[];
  bestPrice: string | null;
  baselinePrice: string | null;
  bestSavings: string | null;
  searchTime: string;
}

interface FlightRoute {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate: string;
  passengers: number;
  cabinClass: string;
}

interface FlightResultsProps {
  flights?: FlightResult[];
  summary?: FlightSearchSummary;
  route?: FlightRoute;
  success?: boolean;
  error?: string;
}

const SAMPLE_DATA: FlightResultsProps = {
  success: true,
  flights: [
    {
      id: "sample1",
      airline: "ANA",
      price: "$487.00",
      priceNumeric: 487,
      savings: "38.3% off (save $302.00)",
      savingsPercent: 38.3,
      departureTime: "10:30 AM",
      arrivalTime: "3:45 PM +1",
      duration: "11h 15m",
      stops: "Nonstop",
      foundIn: "India",
    },
    {
      id: "sample2",
      airline: "Japan Airlines",
      price: "$512.00",
      priceNumeric: 512,
      savings: "35.1% off (save $277.00)",
      savingsPercent: 35.1,
      departureTime: "1:15 PM",
      arrivalTime: "6:30 PM +1",
      duration: "11h 15m",
      stops: "Nonstop",
      foundIn: "Mexico",
    },
    {
      id: "sample3",
      airline: "United",
      price: "$545.00",
      priceNumeric: 545,
      savings: "30.9% off (save $244.00)",
      savingsPercent: 30.9,
      departureTime: "8:00 AM",
      arrivalTime: "2:30 PM +1",
      duration: "12h 30m",
      stops: "1 stop",
      foundIn: "Brazil",
    },
  ],
  summary: {
    totalResults: 15,
    countriesSearched: ["India", "Mexico", "Brazil", "Thailand", "Turkey"],
    bestPrice: "$487.00",
    baselinePrice: "$789.00",
    bestSavings: "38.3%",
    searchTime: "12.5 seconds",
  },
  route: {
    origin: "LAX",
    destination: "NRT",
    departureDate: "2025-03-15",
    returnDate: "2025-03-22",
    passengers: 1,
    cabinClass: "economy",
  },
};

export function FlightResults({
  flights = SAMPLE_DATA.flights,
  summary = SAMPLE_DATA.summary,
  route = SAMPLE_DATA.route,
  success = true,
  error,
}: FlightResultsProps) {
  if (!success || error) {
    return (
      <div className="flex w-full flex-col gap-3 overflow-hidden rounded-2xl bg-gradient-to-br from-red-500 to-red-600 p-4 shadow-lg">
        <div className="flex items-center gap-2 text-white">
          <PlaneIcon size={24} />
          <span className="font-medium">Flight Search Error</span>
        </div>
        <p className="text-white/80 text-sm">{error || "Unable to search for flights. Please try again."}</p>
      </div>
    );
  }

  if (!flights || flights.length === 0) {
    return (
      <div className="flex w-full flex-col gap-3 overflow-hidden rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 p-4 shadow-lg">
        <div className="flex items-center gap-2 text-white">
          <PlaneIcon size={24} />
          <span className="font-medium">No Flights Found</span>
        </div>
        <p className="text-white/80 text-sm">No flights found for this route. Try different dates or destinations.</p>
      </div>
    );
  }

  return (
    <div className="flex w-full flex-col gap-3 overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 p-4 shadow-lg backdrop-blur-sm">
      <div className="absolute inset-0 bg-white/10 backdrop-blur-sm" />

      <div className="relative z-10">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <PlaneIcon size={24} />
            <span className="font-medium">
              {route?.origin} → {route?.destination}
            </span>
          </div>
          <div className="text-white/70 text-xs">
            {route?.departureDate} {route?.returnDate !== "One-way" && `- ${route?.returnDate}`}
          </div>
        </div>

        {summary?.bestSavings && (
          <div className="mb-3 flex items-center gap-2 rounded-lg bg-white/20 px-3 py-2">
            <SavingsIcon size={18} />
            <span className="font-medium text-white text-sm">
              Save up to {summary.bestSavings} compared to US prices!
            </span>
          </div>
        )}

        <div className="space-y-2">
          {flights.slice(0, 5).map((flight, index) => (
            <div
              key={flight.id}
              className={cx(
                "flex items-center justify-between rounded-xl bg-white/15 p-3 backdrop-blur-sm transition-all hover:bg-white/25",
                { "ring-2 ring-yellow-300/50": index === 0 }
              )}
            >
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{flight.airline}</span>
                  {index === 0 && (
                    <span className="rounded bg-yellow-400/90 px-1.5 py-0.5 font-medium text-xs text-yellow-900">
                      BEST DEAL
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-white/70 text-xs">
                  <span>{flight.departureTime} - {flight.arrivalTime}</span>
                  <span>•</span>
                  <span>{flight.duration}</span>
                  <span>•</span>
                  <span>{flight.stops}</span>
                </div>
                <div className="text-white/60 text-xs">Found in {flight.foundIn}</div>
              </div>

              <div className="text-right">
                <div className="font-bold text-white text-lg">{flight.price}</div>
                {flight.savings && (
                  <div className="text-emerald-200 text-xs">{flight.savings}</div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-3 flex flex-wrap justify-between gap-2 text-white/60 text-xs">
          <div>
            Searched: {summary?.countriesSearched?.join(", ")}
          </div>
          <div>
            {summary?.totalResults} results in {summary?.searchTime}
          </div>
        </div>
      </div>
    </div>
  );
}
