"""
Python 3.+

Coursera Financial Engineering Part 1, Week 4 Quiz

Generate option prices from stonk movement, calibrated for
black-scholes model.

"""
import math

class calibrated_binom_tree(object):
    def __init__(self, stock_price, volatility,
                 mature_date, dividend, rate, strike, period_lim):

        self.stock_price = stock_price;
        self.strike = strike;
        self.sigma = volatility;

        self.T = mature_date;
        self.c = dividend;
        self.n = period_lim;
        self.r = rate;

        # stonk movement rate u (1/u = d)
        # and risk free probabilities calibrated for black-scholes model
        self.u = math.exp(self.sigma*math.sqrt(self.T/self.n));
        self.cal_q = (math.exp((self.r-self.c)*self.T/self.n)- +\
                     (1/self.u)) / (self.u-(1/self.u));

    def futures_value(self, Cu, Cd):
        return Cu*self.cal_q + Cd*(1-self.cal_q);

    def options_value(self, Cu, Cd):
        return round(math.exp(-self.r*(self.T/self.n)),4)*self.futures_value(Cu, Cd);

    def make_stock_lattice(self):
        stock_lattice = {"t="+str(i):[] for i in range(self.n+1)}

        for k in range(0, self.n+1):
            for j in range(k+1):
                price = self.stock_price*(self.u**(k-j))*((1/self.u)**j);
                stock_lattice["t="+str(k)].append(round(price,4));
        return stock_lattice

    def make_future_lattice(self, lattice):
        l = self.n;

        future_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        future_lattice["t="+str(l)] = lattice["t="+str(l)]

        while(l>0):
            for s in range(l):
                Cu = future_lattice["t="+str(l)][s]
                Cd = future_lattice["t="+str(l)][s+1]

                future = self.futures_value(Cu, Cd);
                future_lattice["t="+str(l-1)].append(round(future,4))
            l-=1;
        return future_lattice;

    def make_options_lattice(self, lattice, is_call, is_choose, is_american):
        early_ex = self.n; l = self.n;
        t = 1;
        if not is_call: t*=-1;

        option_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        option_lattice["t="+str(l)] = [max(round(t*(i-self.strike),4), 0) for i in lattice["t="+str(l)] ]

        if is_choose:
            option_lattice["t="+str(l)] = [i for i in lattice["t="+str(l)] ]

        while(l>0):
            for s in range(l):
                Cu = option_lattice["t="+str(l)][s]
                Cd = option_lattice["t="+str(l)][s+1]
                strike_dif = t*(lattice["t="+str(l-1)][s]-self.strike)
                option_price = self.options_value(Cu, Cd)

                if is_american and (strike_dif>option_price) and (l-1<early_ex):
                    early_ex = l-1;
                    option_price = self.options_value(Cu, Cd)

                option = max(strike_dif, option_price)
                option_lattice["t="+str(l-1)].append(round(option,4))

            l-=1;

        if is_american and early_ex < self.n: print("* Early exercise t="+str(early_ex))
        return option_lattice;

    def make_choose_lattice(self, lattice, is_american):

        call_lattice    = self.make_options_lattice(lattice=lattice,
                                                        is_call=True, is_choose=False, is_american=is_american)
        put_lattice     = self.make_options_lattice(lattice=lattice,
                                                        is_call=False, is_choose=False, is_american=is_american)

        choose_option_lattice = {"t="+str(i):[] for i in range(self.n+1)}

        l = self.n
        while(l>=0):
            for s in zip(call_lattice["t="+str(l)], put_lattice["t="+str(l)]):
                choose_option_lattice["t="+str(l)].append(max(s))
            l-=1;
        return choose_option_lattice

    def print_lattice(self, lattice):
        for x in lattice: print(x, lattice[x]);

    def put_call_parity(self, put, call):
        p = put + self.stock_price*math.exp(-self.c*self.T)
        c = call + self.strike*math.exp(-self.r*self.T)
        return p, c


# init the tree with parameters
# as per quiz instructions
t = calibrated_binom_tree(
               stock_price = 100,
               volatility = 0.30,
               mature_date = 0.25,
               dividend = 0.01,
               rate = 0.02,
               strike = 110,
               period_lim = 15);

# first, generate the stonks lattice from which we can answer the following
# quiz questions
stocks_lattice = t.make_stock_lattice()

# Question 1
# Compute the fair value of an American call option, strike 110, n = 15
options_lattice = t.make_options_lattice(stocks_lattice,
                                            is_call=True, is_choose=False, is_american=True)
call_price = options_lattice["t=0"];
print("Q1 : Price is " + str(*call_price) + "\n")

# Question 2
# Compute the fair value of an American put option, strike 110, n = 15
options_lattice = t.make_options_lattice(stocks_lattice,
                                            is_call=False, is_choose=False, is_american=True)
put_price = options_lattice["t=0"];
print("Q2 : Price is " + str(*put_price) + "\n")

# Question 3 & 4
# is it optimal to exercise the American put option early?
print ("Q3 & Q4 : Yes, t = 5 \n")

# Question 5
# put call parity?
p, c = t.put_call_parity(*put_price, *call_price)
print("Q5 : put, call parity is {0} , {1}".format(round(p,2), round(c,2)) + "\n")

# Question 6
# compute the fair value of an American call option, strike 110, n = 10
# on a futures contract that expires n = 10
futures_lattice = t.make_future_lattice(stocks_lattice)
t.n = 10; #adjust the period for the new contract, from 15 to 10
options_lattice = t.make_options_lattice(futures_lattice,
                                            is_call=True, is_choose=False, is_american=True)
call_on_future_price = options_lattice["t=0"]
print("Q6 : Price is " + str(*call_on_future_price) + "\n")

# Question 7
# What is the early exercise date?
print("Q7 : Yes, t = 7 \n")

# Question 8
# Compute the value of a choose option that expires after 10 periods
# (chooser option compares a put lattice to a call lattice and keeps the
# most profitable option for each stock value at each period)
# on a future contract that expires after 15 periods with strike = 100.
t.strike = 100; t.n = 15
choose_lattice = t.make_choose_lattice(futures_lattice, is_american=False)
t.n = 10 #adjust the period for the new contract, from 15 to 10
choose_option_lattice = t.make_options_lattice(choose_lattice, is_call=True, is_choose=True,  is_american=False)
print("Q8 : Price is "+str(*choose_option_lattice["t=0"]) )
