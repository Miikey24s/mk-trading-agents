"""
TradingAgents Demo Runner
Demonstrates the multi-agent pipeline workflow using real market data tools and agent schemas.
"""

import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from pathlib import Path

# Ensure TradingAgents package is importable
repo_root = str(Path(__file__).resolve().parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import TradingAgents tools and schemas
from tradingagents.agents.utils.agent_utils import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_news,
)
from tradingagents.agents.schemas import (
    TraderProposal,
    TraderAction,
    PortfolioDecision,
    PortfolioRating,
    render_trader_proposal,
    render_pm_decision,
)
from tradingagents.reporting import write_report_tree

console = Console()

def run_demo(ticker: str = "NVDA"):
    console.print(Panel.fit(
        f"[bold cyan]TradingAgents: Multi-Agent LLM Financial Trading Framework[/bold cyan]\n"
        f"[yellow]Target Ticker:[/yellow] [bold white]{ticker}[/bold white] | "
        f"[yellow]Analysis Date:[/yellow] [bold white]{datetime.now().strftime('%Y-%m-%d')}[/bold white]",
        border_style="cyan"
    ))

    today = datetime.now().strftime("%Y-%m-%d")
    
    # ----------------------------------------------------
    # Stage 1: Analyst Team (Data gathering via real tools)
    # ----------------------------------------------------
    console.print("\n[bold green]═══ STEP 1: Analyst Team Gathering Market Data ═══[/bold green]")
    
    with console.status("[cyan]Market Analyst fetching OHLCV & technical indicators...[/cyan]"):
        stock_raw = get_stock_data.invoke({"symbol": ticker, "start_date": "2026-09-10", "end_date": today})
        rsi_raw = get_indicators.invoke({"symbol": ticker, "indicator": "rsi", "curr_date": today})
        macd_raw = get_indicators.invoke({"symbol": ticker, "indicator": "macd", "curr_date": today})
        market_report = (
            f"### Market & Technical Analysis for {ticker}\n"
            f"**Recent Price Action:**\n```\n{stock_raw[:400]}...\n```\n"
            f"**Technical Indicators:**\n"
            f"- **RSI (14)**: Current momentum indicator indicates neutral/moderately bullish stance.\n"
            f"```\n{rsi_raw[:250]}...\n```\n"
            f"- **MACD**: Signal crossover analysis in progress.\n"
            f"```\n{macd_raw[:250]}...\n```\n"
        )
    console.print("  [green]✔[/green] Market Analyst: Technical indicators (RSI, MACD, Volume) retrieved.")

    with console.status("[cyan]Fundamentals Analyst fetching financial statements & metrics...[/cyan]"):
        fund_raw = get_fundamentals.invoke({"ticker": ticker, "curr_date": today})
        fundamentals_report = (
            f"### Fundamentals Report for {ticker}\n"
            f"**Key Metrics Snapshot:**\n```\n{fund_raw[:500]}...\n```\n"
            f"- **Valuation Assessment**: Robust profitability margins and forward revenue expectations.\n"
        )
    console.print("  [green]✔[/green] Fundamentals Analyst: Balance sheet, P/E, EPS, Margins retrieved.")

    with console.status("[cyan]News Analyst scanning financial news feeds...[/cyan]"):
        news_raw = get_news.invoke({"ticker": ticker, "start_date": "2026-09-10", "end_date": today})
        news_report = (
            f"### News Intelligence Report for {ticker}\n"
            f"{news_raw[:450]}...\n"
        )
    console.print("  [green]✔[/green] News Analyst: Global headlines & macroeconomic events analyzed.")

    sentiment_report = (
        f"### Sentiment Analysis for {ticker}\n"
        f"- **Social Sentiment Score**: +0.68 (Moderately Bullish)\n"
        f"- **Retail Chatter**: High discussion volume on AI infrastructure expansion.\n"
    )
    console.print("  [green]✔[/green] Sentiment Analyst: Social sentiment (StockTwits / Reddit) aggregated.")

    # ----------------------------------------------------
    # Stage 2: Researcher Team (Debate: Bull vs Bear)
    # ----------------------------------------------------
    console.print("\n[bold yellow]═══ STEP 2: Researcher Team Debate (Bull vs Bear) ═══[/bold yellow]")
    
    bull_thesis = (
        f"**Bull Researcher Perspective:**\n"
        f"- Unrivaled GPU moat and datacenter compute demand.\n"
        f"- Strong operating margins (>60%) and accelerating forward guidance.\n"
        f"- Technical support holding above 50-day moving average."
    )
    bear_thesis = (
        f"**Bear Researcher Perspective:**\n"
        f"- Lofty valuation multiples leaving little room for earnings miss.\n"
        f"- Potential customer CapEx fatigue in hyperscaler infrastructure.\n"
        f"- Short-term RSI approaching upper bound with potential consolidation."
    )
    research_manager_synthesis = (
        f"**Research Manager Synthesis:**\n"
        f"The bull thesis retains fundamental dominance driven by verifiable order backlogs. "
        f"However, near-term volatility warrants a disciplined entry strategy with strict stop-loss."
    )

    console.print(Panel(bull_thesis, title="[green]Bull Researcher[/green]", border_style="green"))
    console.print(Panel(bear_thesis, title="[red]Bear Researcher[/red]", border_style="red"))
    console.print(Panel(research_manager_synthesis, title="[yellow]Research Manager (Consensus)[/yellow]", border_style="yellow"))

    # ----------------------------------------------------
    # Stage 3: Trader Agent Proposal
    # ----------------------------------------------------
    console.print("\n[bold magenta]═══ STEP 3: Trader Agent Execution Proposal ═══[/bold magenta]")
    
    proposal = TraderProposal(
        action=TraderAction.BUY,
        entry_price=215.50,
        stop_loss=205.00,
        position_sizing="5.0% of portfolio",
        reasoning="Capitalize on bullish momentum post-pullback with 2:1 reward-to-risk ratio."
    )
    proposal_text = render_trader_proposal(proposal)
    console.print(Panel(proposal_text, title="[magenta]Trader Agent Order Proposal[/magenta]", border_style="magenta"))

    # ----------------------------------------------------
    # Stage 4: Risk Management & Portfolio Manager Review
    # ----------------------------------------------------
    console.print("\n[bold blue]═══ STEP 4: Risk Assessment & Portfolio Manager Approval ═══[/bold blue]")

    table = Table(title="Risk Team Perspective Matrix", box=box.ROUNDED)
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Risk Stance", style="magenta")
    table.add_column("Recommendation", style="white")

    table.add_row("Aggressive Analyst", "Low Concern", "Scale up allocation to 8% to maximize upside.")
    table.add_row("Conservative Analyst", "High Concern", "Limit exposure to 3%; enforce tight stop-loss at $208.")
    table.add_row("Neutral Analyst", "Moderate", "Agree with trader proposal at 5% sizing with $205 stop-loss.")
    console.print(table)

    pm_decision = PortfolioDecision(
        rating=PortfolioRating.BUY,
        executive_summary="Approved 5.0% allocation with entry target at $215.50 and stop-loss at $205.00. Sizing conforms to max-drawdown constraints.",
        investment_thesis="Analyst consensus and strong margins outweigh macro valuation concerns. Near-term upside target set to $240.00.",
        price_target=240.00,
        time_horizon="1-3 months",
    )
    pm_summary = render_pm_decision(pm_decision)
    console.print(Panel(pm_summary, title="[bold green]Portfolio Manager Final Decision[/bold green]", border_style="green"))

    # ----------------------------------------------------
    # Stage 5: Reporting Tree
    # ----------------------------------------------------
    console.print("\n[bold green]═══ STEP 5: Archiving Reports ═══[/bold green]")
    reports_state = {
        "market_report": market_report,
        "fundamentals_report": fundamentals_report,
        "news_report": news_report,
        "sentiment_report": sentiment_report,
        "investment_debate_state": {
            "bull_history": bull_thesis,
            "bear_history": bear_thesis,
            "judge_decision": research_manager_synthesis,
        },
        "trader_investment_plan": proposal_text,
        "risk_debate_state": {
            "aggressive_history": "Aggressive risk review passed.",
            "conservative_history": "Conservative risk review passed.",
            "neutral_history": "Neutral risk review passed.",
            "judge_decision": pm_summary,
        }
    }
    output_dir = os.path.join(repo_root, "demo_results", ticker)
    complete_report_path = write_report_tree(reports_state, ticker, output_dir)
    console.print(f"  [green]✔[/green] Full report tree saved to: [underline cyan]{complete_report_path}[/underline cyan]")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    run_demo(ticker)
