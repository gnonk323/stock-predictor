"use client"

import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  Plus,
  Minus,
  Equal,
  ArrowUp,
  ArrowDown,
  RotateCw,
} from "lucide-react"
import { useState } from "react"
import axios from "axios"


interface RowProps {
  ticker: string
  companyName: string
  openPrice: string
  sentimentScore: string
  projectedChange: string
}

function Row({ ticker, companyName, openPrice, sentimentScore, projectedChange }: RowProps) {
  let badgeVariant: "neutral" | "positive" | "negative" = "neutral";

  try {
    const sentiment = parseFloat(sentimentScore);
    if (sentiment > 0.25) {
      badgeVariant = "positive";
    } else if (sentiment < -0.25) {
      badgeVariant = "negative";
    }
  } catch (e) {
    console.error("Error parsing sentiment score", e);
  }

  return (
    <TableRow>
      <TableCell>
        <p className="font-semibold">{ticker}</p>
        <p className="text-sm">{companyName}</p>
      </TableCell>
      <TableCell className={openPrice === undefined ? "text-red-500 italic" : undefined}>{openPrice === undefined ? "API Call Failed" : `$${openPrice}`}</TableCell>
      <TableCell>
        <Badge variant={badgeVariant}>
          {badgeVariant === "positive" ? <Plus size={16} className="mr-2" /> : badgeVariant === "negative" ? <Minus size={16} className="mr-2" /> : <Equal size={16} className="mr-2" />}
          {badgeVariant === "positive" ? "Positive" : badgeVariant === "negative" ? "Negative" : "Neutral"}
        </Badge>
      </TableCell>
      <TableCell>
      <div className="flex items-center">
          {projectedChange !== undefined ? projectedChange.includes("-") ? <ArrowDown size={16} className="mr-2 text-red-500" /> : <ArrowUp size={16} className="mr-2 text-green-500" /> : null}
          <span className={projectedChange === undefined ? "text-red-500 italic" : projectedChange.includes("-") ? "text-red-500" : "text-green-500"}>{projectedChange === undefined ? "API Call Failed" : projectedChange}</span>
        </div>
      </TableCell>
    </TableRow>
  )
}


interface StockPrediction {
  symbol: string
  companyName: string
  openPrice: string
  sentimentScore: string
  predictedChange: string
}

export default function Home() {

  const stocks: { [key: string]: string } = {
    'AAPL': 'Apple',
    'NVDA': 'NVIDIA',
    'MSFT': 'Microsoft',
    'AMZN': 'Amazon',
    'META': 'Meta',
    'GOOGL': 'Alphabet',
    'TSLA': 'Tesla',
    'ORCL': 'Oracle',
    'AMD': 'AMD',
    'NFLX': 'Netflix'
  }

  const stocksDummy: { [key: string]: string[] } = {
    'AAPL': ['Apple', '227.78', '0.00', '-0.04%'],
    'NVDA': ['NVIDIA', '131.91', '-0.57', '-0.25%'],
    'MSFT': ['Microsoft', '415.23', '0.44', '0.05%'],
    'AMZN': ['Amazon', '187.13', '0.87', '0.34%'],
    'META': ['Meta', '587.57', '0.00', '-0.04%'],
    'GOOGL': ['Alphabet', '162.11', '0.64', '-0.08%'],
    'TSLA': ['Tesla', '241.81', '-0.34', '-0.07%'],
    'ORCL': ['Oracle', '177.65', '0.80', '0.34%'],
    'AMD': ['AMD', '169.76', '0.42', '0.04%'],
    'NFLX': ['Netflix', '723.29', '-0.34', '-0.07%']
  }

  const dummyPredictions: StockPrediction[] = Object.keys(stocksDummy).map((symbol) => {
    return {
      symbol: symbol,
      companyName: stocksDummy[symbol][0],
      openPrice: stocksDummy[symbol][1],
      sentimentScore: stocksDummy[symbol][2],
      predictedChange: stocksDummy[symbol][3]
    };
  })

  const [stockPredictions, setStockPredictions] = useState<StockPrediction[]>([])

  const fetchStockPredictions = async () => {
    try {
      const promises = Object.keys(stocks).map(async (symbol) => {
        const companyName = stocks[symbol];
        const response = await axios.get(`http://localhost:8000/get_stock_prediction`, {
          params: {
            company_name: companyName,
            symbol: symbol
          }
        });
        return {
          symbol: symbol,
          companyName: companyName,
          openPrice: response.data.open_price,
          sentimentScore: response.data.sentiment_score,
          predictedChange: response.data.predicted_change
        };
      });
      const results = await Promise.all(promises);
      setStockPredictions(results);
      console.log("Fetched stock predictions", results);
    } catch (e) {
      console.error("Error fetching stock predictions", e);
    }
  }

  return (
    <div className="flex justify-center mx-28 mt-8 flex-col">
      <div className="flex justify-between w-full">
        <h1 className="text-4xl font-bold">Featured</h1>
        <Button
          onClick={
            async () => {
              await fetchStockPredictions();
            }
          }
        >
          <RotateCw size={16} className="mr-2" />
          Refresh
        </Button>
      </div>
      <br />
      <div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Symbol</TableHead>
              <TableHead>Open Price</TableHead>
              <TableHead>Sentiment</TableHead>
              <TableHead>Projected Change</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* {stockPredictions.map((prediction) => (
              <Row
                key={prediction.symbol}
                ticker={prediction.symbol}
                companyName={stocks[prediction.symbol]}
                openPrice={prediction.openPrice}
                sentimentScore={prediction.sentimentScore}
                projectedChange={prediction.predictedChange}
              />
            ))} */}
            {dummyPredictions.map((prediction) => (
              <Row
                key={prediction.symbol}
                ticker={prediction.symbol}
                companyName={prediction.companyName}
                openPrice={prediction.openPrice}
                sentimentScore={prediction.sentimentScore}
                projectedChange={prediction.predictedChange}
              />
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
