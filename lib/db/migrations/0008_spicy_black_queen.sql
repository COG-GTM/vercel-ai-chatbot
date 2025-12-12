CREATE TABLE IF NOT EXISTS "FlightPriceCache" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"origin" varchar(3) NOT NULL,
	"destination" varchar(3) NOT NULL,
	"departureDate" date NOT NULL,
	"returnDate" date,
	"cabinClass" varchar(20) DEFAULT 'economy',
	"resultsJson" json NOT NULL,
	"createdAt" timestamp DEFAULT now() NOT NULL,
	"expiresAt" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "FlightSearches" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"chatId" uuid NOT NULL,
	"userId" uuid NOT NULL,
	"origin" varchar(3) NOT NULL,
	"destination" varchar(3) NOT NULL,
	"departureDate" date NOT NULL,
	"returnDate" date,
	"passengers" integer DEFAULT 1 NOT NULL,
	"cabinClass" varchar(20) DEFAULT 'economy',
	"bestPrice" real,
	"baselinePrice" real,
	"savingsPercent" real,
	"resultsCount" integer,
	"searchTimeSeconds" real,
	"createdAt" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "FlightSearches" ADD CONSTRAINT "FlightSearches_chatId_Chat_id_fk" FOREIGN KEY ("chatId") REFERENCES "public"."Chat"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "FlightSearches" ADD CONSTRAINT "FlightSearches_userId_User_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
