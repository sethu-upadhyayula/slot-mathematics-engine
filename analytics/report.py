from analytics.statistics import GameStatistics


def print_statistics_report(stats: GameStatistics, title: str = "Game Statistics") -> None:
    print(f"=== {title} ({stats.num_spins:,} spins) ===")
    print()
    print("Basic metrics")
    print(f"  RTP:                       {stats.rtp:.4%}")
    print(f"  House edge:                {stats.house_edge:.4%}")
    print(f"  Hit frequency:             {stats.hit_frequency:.4%}")
    print(f"  Scatter trigger frequency: {stats.scatter_trigger_frequency:.4%}")
    print(f"  Max win:                   {stats.max_win_multiplier:.1f}x")
    print()
    print("Distribution metrics")
    print(f"  Std dev:                   {stats.std_dev:.4f}")
    print(f"  Variance:                  {stats.variance:.4f}")
    print(f"  Coefficient of variation:  {stats.coefficient_of_variation:.4f}")
    print(f"  Skewness:                  {stats.skewness:.4f}")
    print(f"  Excess kurtosis:           {stats.kurtosis:.4f}")
    print(f"  Median win:                {stats.median_win_multiplier:.2f}x")
    print(f"  90th percentile:           {stats.percentiles[90]:.2f}x")
    print(f"  99th percentile:           {stats.percentiles[99]:.2f}x")
    print(f"  99.9th percentile:         {stats.percentiles[99.9]:.2f}x")
    print()
    print("Win size histogram")
    total = sum(stats.win_histogram.values())
    for label, count in stats.win_histogram.items():
        share = count / total
        bar = "#" * int(share * 50)
        print(f"  {label:>14}: {count:>9,} ({share:.4%}) {bar}")
    print()
    print("Symbol frequency (share of all visible cells)")
    for symbol, freq in sorted(stats.symbol_frequency.items(), key=lambda kv: -kv[1]):
        print(f"  {symbol:<8}: {freq:.4%}")
