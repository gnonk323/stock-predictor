"use client"

import { SearchInput } from "@/components/ui/input"
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
} from "lucide-react"
import { useState, useEffect } from "react"
import axios from "axios"


interface RowProps {
  ticker: string
  companyName: string
  openPrice: string
  sentiment: string
  projectedChange: string
}

function Row({ ticker, companyName, openPrice, sentiment, projectedChange }: RowProps) {
  const badgeVariant = sentiment === "Positive" ? "positive" : sentiment === "Negative" ? "negative" : "neutral"
  return (
    <TableRow>
      <TableCell>
        <p className="font-semibold">{ticker}</p>
        <p className="text-sm">{companyName}</p>
      </TableCell>
      <TableCell>{openPrice}</TableCell>
      <TableCell>
        <Badge variant={badgeVariant}>
          {badgeVariant === "positive" ? <Plus size={16} className="mr-2" /> : badgeVariant === "negative" ? <Minus size={16} className="mr-2" /> : <Equal size={16} className="mr-2" />}
          {sentiment}
        </Badge>
      </TableCell>
      <TableCell>
      <div className="flex items-center">
          {/* {projectedChange.includes("+") ? <ArrowUp size={16} className="mr-2 text-green-500" /> : <ArrowDown size={16} className="mr-2 text-red-500" />} */}
          <span>{projectedChange}</span>
        </div>
      </TableCell>
    </TableRow>
  )
}


interface StockPrediction {
  symbol: string
  companyName: string
  openPrice: string
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

  const [stockPredictions, setStockPredictions] = useState<StockPrediction[]>([])

  const [message, setMessage] = useState<string>("")

  useEffect(() => {
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
            predictedChange: response.data.predicted_change
          };
        });
        const results = await Promise.all(promises);
        setStockPredictions(results);
      } catch (e) {
        console.error("Error fetching stock predictions", e);
      }
    }

    fetchStockPredictions();


    // const fetchMessage = async () => {
    //   try {
    //     const response = await axios.get(`http://localhost:8000/test`);
    //     setMessage(response.data.message);
    //   } catch (e) {
    //     console.error("Error fetching message", e);
    //   }
    // }

    // fetchMessage();
  }, [])

  return (
    <div className="flex justify-center mx-28 mt-8 flex-col">
      <div className="flex justify-between w-full">
        <h1 className="text-4xl font-bold">Featured</h1>
        <SearchInput placeholder="Search" />
      </div>
      <br />
      <h1>{message}</h1>
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
            {stockPredictions.map((prediction) => (
              <Row
                key={prediction.symbol}
                ticker={prediction.symbol}
                companyName={stocks[prediction.symbol]}
                openPrice={prediction.openPrice}
                sentiment="not implemented"
                projectedChange={prediction.predictedChange}
              />
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
