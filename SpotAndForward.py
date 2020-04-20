
import math

def present_value(cashflow, rate, period, time_zero_deposit):
    res = 0
    if time_zero_deposit: res+=cashflow;
    res += sum([ cashflow/((1+rate)**k) for k in range(1,period)])
    return res;

def compound(rate, period, term):
    return (( 1 + (rate/period) )**(term*period));

def discount(rate, period, term):
    return 1/compound(rate, period, term)

def sum_of_discounts(rate_array, period, term):
    return sum([ discount(rate, period, k) for k,rate in enumerate(rate_array, 1)])

def difference_in_annual_spot_rates(rate_one, term_one, rate_two, term_two):
    return (compound(rate_two, 1, term_two) / compound(rate_one, 1, term_one))**(term_two - term_one) - 1

def forward_price(value, rate, period, term):
    return value*compound(rate, period, term) #stock_price * discount rate
