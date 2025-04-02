Here's a Python implementation to detect long weekends with middle day identification, handling month boundaries and holiday combinations:

```python
from datetime import date, timedelta
import calendar

def find_long_weekends(target_year, target_month, holidays):
    # Calculate date range covering target month + buffer days
    first_day = date(target_year, target_month, 1)
    last_day = date(target_year, target_month, 
                   calendar.monthrange(target_year, target_month)[1])
    start_range = first_day - timedelta(days=2)
    end_range = last_day + timedelta(days=2)
    
    # Generate all dates in range and identify non-working days
    current_date = start_range
    non_working_dates = []
    holidays_set = set(holidays)
    
    while current_date = 5 or current_date in holidays_set:
            non_working_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Find consecutive sequences of non-working days
    sequences = []
    if not non_working_dates:
        return []
    
    current_seq = [non_working_dates[0]]
    for d in non_working_dates[1:]:
        if (d - current_seq[-1]).days == 1:
            current_seq.append(d)
        else:
            if len(current_seq) >= 3:
                sequences.append(current_seq)
            current_seq = [d]
    if len(current_seq) >= 3:
        sequences.append(current_seq)
    
    # Filter sequences affecting target month and format results
    long_weekends = []
    for seq in sequences:
        if any(d.month == target_month and d.year == target_year for d in seq):
            start = seq[0]
            end = seq[-1]
            middle_days = seq[1:-1]
            
            long_weekends.append({
                'start': start,
                'end': end,
                'middle_days': middle_days,
                'total_days': len(seq),
                'crosses_month': start.month != end.month
            })
    
    return long_weekends
```

Key features of this implementation:
- **Month boundary handling**: Checks 2 days before/after the target month
- **Middle day identification**: Explicitly marks days between start and end
- **Holiday/weekend combination**: Treats weekends and holidays equally as non-working days
- **Cross-month tracking**: Flags weekends spanning multiple months

Example usage for March 2024 (with Easter):
```python
# Sample holidays including Easter period
holidays = [
    date(2024, 3, 29),  # Good Friday
    date(2024, 4, 1),   # Easter Monday
    date(2024, 1, 1),   # New Year's Day
]

result = find_long_weekends(2024, 3, holidays)
for lw in result:
    print(f"Long weekend from {lw['start']} to {lw['end']}")
    print(f"Middle days: {[d.strftime('%Y-%m-%d') for d in lw['middle_days']]}")
```

The algorithm handles complex cases like:
- **Bridge holidays**: Thursday-Friday holidays connecting to weekends
- **Month transitions**: Sequences like December 30-31 to January 1
- **Variable-length weekends**: From 3-day weekends to longer sequences

To use this in production, you would:
1. Provide comprehensive holiday data across month boundaries
2. Add error handling for invalid inputs
3. Implement caching for repeated queries
4. Add secondary sorting/filtering based on business needs

The solution prioritizes clarity over optimization, making it suitable for typical scheduling system loads. For high-volume applications, consider precomputing non-working days and using interval trees for faster lookups.

