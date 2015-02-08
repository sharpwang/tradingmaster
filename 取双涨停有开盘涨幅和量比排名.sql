select t1.stock_code, t1.ymd, 100.0 * (t1.close1 - t1.open1) / t1.open1 from market.lday t1 
where t1.open1 < t1.preclose * 1.03 
and exists (select 1 from market.lday t0
    where t1.exchange_code = t0.exchange_code and t1.stock_code = t0.stock_code
    and t0.volumn / t0.prevolumn between 0.5 and 2.0
    and t1.bar + 1 = t0.bar and t0.rzdt = 2) limit 0,10000;