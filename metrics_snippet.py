# metrics_snippet.py

def print_backtest_metrics(strat):
    
    print("\n" + "-"*30)
    print("Algo Metrics")
    print("-"*30)
    
    try:
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_val = sharpe.get('sharperatio')
        if sharpe_val is not None:
            print(f"Sharpe Ratio: {sharpe_val:.2f}")
        else:
            print("Sharpe Ratio: N/A (Needs more trades or variance)")
    except Exception:
        print("Sharpe Ratio: Error calculating")
    
    try:
        dd = strat.analyzers.drawdown.get_analysis()
        print(f"Max Drawdown: {dd.max.drawdown:.2f}%")
    except Exception:
        print("Max Drawdown: Error calculating")
    
    try:
        trades = strat.analyzers.trades.get_analysis()
        total_closed = trades.get('total', {}).get('closed', 0)
        
        print(f"Total Closed Trades: {total_closed}")
        
        if total_closed > 0:
            won = trades.won.total
            lost = trades.lost.total
            win_rate = (won / total_closed) * 100
            print(f"Wins: {won} | Losses: {lost}")
            print(f"Win Rate: {win_rate:.2f}%")
    except Exception:
        print("Trade Analysis: Error calculating")
        
    print("-"*30 + "\n")