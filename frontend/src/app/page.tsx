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


interface RowProps {
  ticker: string
  companyName: string
  currentPrice: string
  change: string
  sentiment: string
  projectedChange: string
}

function Row({ ticker, companyName, currentPrice, change, sentiment, projectedChange }: RowProps) {
  const badgeVariant = sentiment === "Positive" ? "positive" : sentiment === "Negative" ? "negative" : "neutral"
  return (
    <TableRow>
      <TableCell>
        <p className="font-semibold">{ticker}</p>
        <p className="text-sm">{companyName}</p>
      </TableCell>
      <TableCell>{currentPrice}</TableCell>
      <TableCell>
        <div className="flex items-center">
          {change.includes("+") ? <ArrowUp size={16} className="mr-2 text-green-500" /> : <ArrowDown size={16} className="mr-2 text-red-500" />}
          <span className={change.includes("+") ? "text-green-500" : "text-red-500"}>{change}</span>
        </div>
      </TableCell>
      <TableCell>
        <Badge variant={badgeVariant}>
          {badgeVariant === "positive" ? <Plus size={16} className="mr-2" /> : badgeVariant === "negative" ? <Minus size={16} className="mr-2" /> : <Equal size={16} className="mr-2" />}
          {sentiment}
        </Badge>
      </TableCell>
      <TableCell>
      <div className="flex items-center">
          {projectedChange.includes("+") ? <ArrowUp size={16} className="mr-2 text-green-500" /> : <ArrowDown size={16} className="mr-2 text-red-500" />}
          <span className={projectedChange.includes("+") ? "text-green-500" : "text-red-500"}>{projectedChange}</span>
        </div>
      </TableCell>
    </TableRow>
  )
}


export default function Home() {
  return (
    <div className="flex justify-center mx-28 mt-8 flex-col">
      <div className="flex justify-between w-full">
        <h1 className="text-4xl font-bold">Featured</h1>
        <SearchInput placeholder="Search" />
      </div>
      <br />
      <div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Symbol</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Change</TableHead>
              <TableHead>Sentiment</TableHead>
              <TableHead>Projected Change</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <Row
              ticker="AAPL"
              companyName="Apple Inc."
              currentPrice="$145.86"
              change="+0.86"
              sentiment="Positive"
              projectedChange="+0.50"
            />
            <Row
              ticker="TSLA"
              companyName="Tesla Inc."
              currentPrice="$678.90"
              change="-0.90"
              sentiment="Negative"
              projectedChange="-1.20"
            />
            <Row
              ticker="AMZN"
              companyName="Amazon.com Inc."
              currentPrice="$3,372.20"
              change="+2.20"
              sentiment="Neutral"
              projectedChange="+0.04"
            />
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
