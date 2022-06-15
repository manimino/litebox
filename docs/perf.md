# Performance Analysis

There are many ways to build an index of Python objects. Here is how they compare.

### Baseline

In Python, you'd use a comprehension like `list(obj for obj in objects if obj.x > 0.5 and obj.y < 0.2)`.
There are other ways (e.g. `filter()`), but comprehensions are the fastest, so that's the point of comparison.

### Benchmark

For a 10M object dataset with two numeric indices:

                     | Comprehension      | DuckDB | Sqlite | Pandas | Polars        
-------------------- | ------------------ | ------ | ------ | ------ | --------------
Build 10M item index | 2.2s               | 4s     | 30s    | 15s    | 3.9s          
Python Object size   | 2.6GB              | 2.6GB  | 2.6GB  | 2.6GB  | 2.6GB         
Index RAM size       | N/A                | 1.2GB  | 2.1GB  | 300MB  | 300MB         
Get 1 item           | 0.9s               | 1ms    | 0.16ms | 40ms   | 40ms          
Get 10 items         | 0.9s               | 2ms    | 0.17ms | 38ms   | 40ms          
Get 100 items        | 0.9s               | 20ms   | 0.56ms | 39ms   | 40ms          
Get 1K items         | 0.9s               | 82ms   | 4ms    | 40ms   | 40ms          
Get 10K items        | 0.9s               | 0.12s  | 30ms   | 43ms   | 40ms          
Get 100K items       | 0.9s               | 0.2s   | 0.22s  | 73ms   | 70ms          
Get 1M items         | 0.9s               | 0.8s   | 2.2s   | 0.2s   | 0.21s         
Get 10M items        | 1.13s              | 4.5s   | 21.3s  | 0.6s   | 0.81s         
Update 1 item        | 0.9s               | 1ms    | 0.1ms  | 56ms   | 3.9s
Remove 1 item        | 2.2s               | 1ms    | 0.1ms  | 0.63s  | 3.9s

"Get 1 item" refers to running a `find()` that returns 1 item on average.

### Discussion

**DuckDB** is the all-around winner. It's not the best in any category, but it lacks any major drawback.
It's fast to build. It takes some RAM, but the RAM scales well as you add more columns. It executes queries
in parallel, and uses regular SQL. 

**SQLite** is the race car. It's fastest by far for small queries, thanks to its row-based nature and B-tree indices. 
But it suffers from slow build time, high RAM use (and scales with number of columns), and terrible performance
when the query results in more than 10% of the total items.

**Pandas** offers consistent performance and a very low RAM cost. But it loses to DuckDB because it cannot
execute queries in parallel, takes a longer time to build, offers poor performance on small queries, and
is slow on update / remove operations.

**Polars** has some advantages over pandas. It has a lightning-fast build time, low RAM usage, and parallel query
execution. But due to its immutable nature, changing any data point requires replacing the whole column / dataframe.
And like Pandas, its results on small queries are unimpressive compared to DuckDB.

