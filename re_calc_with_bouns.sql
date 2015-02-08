-- --------------------------------------------------------------------------------
-- Routine DDL
-- --------------------------------------------------------------------------------
DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE `re_calc_with_bouns`()
BEGIN
    declare done0 int default 0;
    declare exchange_code0, stock_code0 varchar(16);
    declare cur0 cursor for
        select exchange_code, stock_code from stock;
    declare continue handler for not found set done0 = 1;
    open cur0;
    loop0: loop
        fetch cur0 into exchange_code0, stock_code0;
        if done0 = 1 then
            leave loop0;
        end if;
        update lday set open1 = open0 , high1 = high0 , low1 = low0 , close1 = close0 
            where exchange_code = exchange_code0 and stock_code = stock_code0;     /*初始值*/   
        begin
            declare done1 int default 0;
            declare ymd1 int default 19800101;
            declare song1, zeng1, pai1, pei1, ppei1 float;
            declare cur1 cursor for
                select ymd, song, zeng, pai, pei, ppei from sharebouns 
                where exchange_code = exchange_code0 and stock_code = stock_code0 order by ymd asc;
            declare continue handler for not found set done1 = 1;
            open cur1;
            loop1: loop
                fetch cur1 into ymd1, song1, zeng1, pai1, pei1, ppei1;
                if done1 = 1 then
                    leave loop1;
                end if;
                update lday set 
                    open1  = ((open1  / 10.0  - pai1) + ppei1 *  pei1) / (10.0 + song1  + zeng1  + pei1 ) * 100.0,
                    high1  = ((high1  / 10.0  - pai1) + ppei1 *  pei1) / (10.0 + song1  + zeng1  + pei1 ) * 100.0,
                    low1   = ((low1   / 10.0  - pai1) + ppei1 *  pei1) / (10.0 + song1  + zeng1  + pei1 ) * 100.0,
                    close1 = ((close1 / 10.0  - pai1) + ppei1 *  pei1) / (10.0 + song1  + zeng1  + pei1 ) * 100.0
                where exchange_code = exchange_code0 and stock_code = stock_code0 and ymd < ymd1;    
            end loop loop1;    
        end;
    end loop loop0;
END
