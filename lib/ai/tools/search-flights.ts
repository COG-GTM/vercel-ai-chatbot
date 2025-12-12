import { tool } from "ai";
import { z } from "zod";

interface FlightResult {
  id: string;
  airline: string;
  price: number;
  currency: string;
  original_price?: number;
  savings_percent?: number;
  savings_amount?: number;
  departure_time: string;
  arrival_time: string;
  duration: string;
  stops: number;
  searched_from_country: string;
}

interface BrainEngineResponse {
  success: boolean;
  flights: FlightResult[];
  total_results: number;
  countries_searched: string[];
  best_price?: number;
  baseline_price?: number;
  best_savings_percent?: number;
  search_time_seconds: number;
  error?: string;
}

export const searchFlights = tool({
  description: `Search for cheap flights using geographic price arbitrage. 
Use this tool when the user wants to:
- Find flights or airfare
- Book travel or trips
- Compare flight prices
- Find the cheapest way to fly somewhere

The tool searches from multiple countries (India, Mexico, Brazil, Thailand, Turkey)
to find prices that are often 10-40% cheaper than standard US/EU prices.

Always ask for origin, destination, and dates if not provided.`,

  inputSchema: z.object({
    origin: z
      .string()
      .length(3)
      .describe("Origin airport IATA code (e.g., LAX, JFK, SFO, ORD)"),
    destination: z
      .string()
      .length(3)
      .describe("Destination airport IATA code (e.g., NRT, LHR, CDG, FCO)"),
    departureDate: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/)
      .describe("Departure date in YYYY-MM-DD format"),
    returnDate: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/)
      .optional()
      .describe("Return date in YYYY-MM-DD format (optional for one-way trips)"),
    passengers: z
      .number()
      .int()
      .min(1)
      .max(9)
      .default(1)
      .describe("Number of passengers (1-9)"),
    cabinClass: z
      .enum(["economy", "premium_economy", "business", "first"])
      .default("economy")
      .describe("Preferred cabin class"),
  }),

  execute: async ({
    origin,
    destination,
    departureDate,
    returnDate,
    passengers,
    cabinClass,
  }) => {
    const brainEngineUrl = process.env.BRAIN_ENGINE_URL;
    const apiKey = process.env.BRAIN_ENGINE_API_KEY;

    if (!brainEngineUrl) {
      return {
        success: false,
        error: "Brain Engine URL not configured. Please set BRAIN_ENGINE_URL.",
        flights: [],
        countries_searched: [],
      };
    }

    if (!apiKey) {
      return {
        success: false,
        error:
          "Brain Engine API key not configured. Please set BRAIN_ENGINE_API_KEY.",
        flights: [],
        countries_searched: [],
      };
    }

    try {
      console.log(
        `[searchFlights] Searching: ${origin} → ${destination} on ${departureDate}`
      );

      const response = await fetch(`${brainEngineUrl}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          origin: origin.toUpperCase(),
          destination: destination.toUpperCase(),
          departureDate,
          returnDate,
          passengers,
          cabinClass,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          `[searchFlights] API error: ${response.status} - ${errorText}`
        );

        return {
          success: false,
          error: `Search failed with status ${response.status}. Please try again.`,
          flights: [],
          countries_searched: [],
        };
      }

      const data: BrainEngineResponse = await response.json();

      console.log(
        `[searchFlights] Found ${data.total_results} flights, ` +
          `best savings: ${data.best_savings_percent}%`
      );

      return {
        success: true,
        flights: data.flights.map((flight) => ({
          id: flight.id,
          airline: flight.airline,
          price: `$${flight.price.toFixed(2)}`,
          priceNumeric: flight.price,
          savings: flight.savings_percent
            ? `${flight.savings_percent}% off (save $${flight.savings_amount?.toFixed(2)})`
            : null,
          savingsPercent: flight.savings_percent,
          departureTime: flight.departure_time,
          arrivalTime: flight.arrival_time,
          duration: flight.duration,
          stops:
            flight.stops === 0
              ? "Nonstop"
              : `${flight.stops} stop${flight.stops > 1 ? "s" : ""}`,
          foundIn: flight.searched_from_country,
        })),
        summary: {
          totalResults: data.total_results,
          countriesSearched: data.countries_searched,
          bestPrice: data.best_price ? `$${data.best_price.toFixed(2)}` : null,
          baselinePrice: data.baseline_price
            ? `$${data.baseline_price.toFixed(2)}`
            : null,
          bestSavings: data.best_savings_percent
            ? `${data.best_savings_percent}%`
            : null,
          searchTime: `${data.search_time_seconds.toFixed(1)} seconds`,
        },
        route: {
          origin: origin.toUpperCase(),
          destination: destination.toUpperCase(),
          departureDate,
          returnDate: returnDate || "One-way",
          passengers,
          cabinClass,
        },
      };
    } catch (error) {
      console.error("[searchFlights] Error:", error);

      return {
        success: false,
        error:
          error instanceof Error
            ? `Search failed: ${error.message}`
            : "An unexpected error occurred while searching for flights.",
        flights: [],
        countries_searched: [],
      };
    }
  },
});
