


'''
Python 3.+

Coursera Financial Engineering Part 1, Week 5 Quiz

Bond pricing and fixed income securities

TODO : maybe someone can add an elementary price lattice?
       it's not necessary for this assignment but it would
       be neat yeah.

'''
import math

class bond_binom_tree(object):
    def __init__(self, short_rate, face_value, ex_coupon,
                 up_rate, down_rate, risk_neutral_prob, period_lim):

        self.f = face_value;
        self.c = ex_coupon;
        self.r = short_rate;
        self.u = up_rate;
        self.d = down_rate;
        self.q = risk_neutral_prob;
        self.n = period_lim;

    def _futures_value(self, Cu, Cd):
        return (Cd*self.q+ Cu*(1-self.q))

    def _forward_value(self, r, Cu, Cd):
        coupon = self.c * self.f
        return self._futures_value(Cu, Cd)/(1+r) + (coupon)

    def _swap_price(self, r, fr, Cu, Cd):
        return ((r - fr) + self._futures_value(Cu, Cd))/(1+r)

    def make_shortrate_lattice(self):
        short_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        short_lattice["t=0"].append(self.r);
        #generate prices moving forward in time.
        for k in range(0, self.n):
            Cd = short_lattice["t="+str(k)][0]*self.d;
            short_lattice["t="+str(k+1)].append(round(Cd,8));
            for j in range(k+1):
                Cu = short_lattice["t="+str(k)][j]*self.u;
                short_lattice["t="+str(k+1)].append(round(Cu,8));

        return short_lattice

    def make_bond_lattice(self, rate_lattice):
        l = self.n
        coupon = self.c*self.f
        bond_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        bond_lattice["t="+str(self.n)] = [self.f+(coupon) for i in range(self.n+1)];

        while (l>0):
            for k in range(l):
                Cd = bond_lattice["t="+str(l)][k]
                Cu = bond_lattice["t="+str(l)][k+1]

                short_rate = rate_lattice["t="+str(l-1)][k]
                bond_price = self._forward_value(short_rate, Cu, Cd)
                bond_lattice["t="+str(l-1)].append(round(bond_price,4))
            l-=1
        return bond_lattice

    def make_forward_or_future_lattice(self, bond_lattice, rate_lattice, is_forward):
        coupon = self.c*self.f
        new_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        new_lattice["t="+str(self.n)] = [i-(coupon) for i in bond_lattice["t="+str(self.n)]]

        l = self.n
        while (l>0):
            for k in range(l):
                Cd = new_lattice["t="+str(l)][k]
                Cu = new_lattice["t="+str(l)][k+1]

                short_rate = rate_lattice["t="+str(l-1)][k]

                if is_forward: value = self._forward_value(short_rate, Cu, Cd)
                else: value = self._futures_value(Cu, Cd)

                new_lattice["t="+str(l-1)].append(round(value,4))
            l-=1
        return new_lattice


    def make_swap_lattice(self, rate_lattice, term_start, fixed_rate):
        new_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        #new_lattice["t="+str(self.n)] = [ round((i-fixed_rate),4) for i in rate_lattice["t="+str(self.n)] ]
        new_lattice["t="+str(self.n)] = [ round((i-fixed_rate) / (1+i),8) for i in rate_lattice["t="+str(self.n)] ]
        l = self.n
        while (l>0):
            for k in range(l):
                Cd = new_lattice["t="+str(l)][k]
                Cu = new_lattice["t="+str(l)][k+1]
                short_rate = rate_lattice["t="+str(l-1)][k]

                value = self._swap_price(short_rate, fixed_rate, Cu, Cd)
                if l-1<term_start:
                    value = self._forward_value(short_rate, Cu, Cd)
                new_lattice["t="+str(l-1)].append(round(value,8))
            l-=1
        return new_lattice

    def make_swaption_lattice(self, swap_lattice, rate_lattice, strike):
        new_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        new_lattice["t="+str(self.n)] = [max((i-strike), 0) for i in swap_lattice["t="+str(self.n)]]
        l = self.n
        while (l>0):
            for k in range(l):
                Cd = new_lattice["t="+str(l)][k]
                Cu = new_lattice["t="+str(l)][k+1]

                short_rate = rate_lattice["t="+str(l-1)][k]

                value = max(self._forward_value(short_rate, Cu, Cd), 0)
                new_lattice["t="+str(l-1)].append(round(value,8))
            l-=1
        return new_lattice

    def make_option_lattice(self, bond_lattice, rate_lattice, is_call, is_american, strike):
        t = 1;
        if not is_call: t*=-1;
        new_lattice = {"t="+str(i):[] for i in range(self.n+1)}
        new_lattice["t="+str(self.n)] = [max(t*(i-strike), 0) for i in bond_lattice["t="+str(self.n)]]

        l = self.n
        while (l>0):
            for k in range(l):
                Cd = new_lattice["t="+str(l)][k]
                Cu = new_lattice["t="+str(l)][k+1]

                short_rate = rate_lattice["t="+str(l-1)][k]
                bond_value = bond_lattice["t="+str(l-1)][k]

                value = max(t*(bond_value-strike), self._forward_value(short_rate, Cu, Cd))
                new_lattice["t="+str(l-1)].append(round(value,4))
            l-=1
        return new_lattice

    def print_lattice(self, lattice):
        for x in lattice: print(x, lattice[x]);

bb = bond_binom_tree(
    short_rate = 0.05,
    face_value = 100,
    ex_coupon = 0,
    up_rate = 1.1,
    down_rate = 0.9,
    risk_neutral_prob = 0.5,
    period_lim = 10)


short_rate_lattice = bb.make_shortrate_lattice()

# Question 1 compute the price of a zero coupon bond, matures at t = 10, face value of 100
bond_lattice = bb.make_bond_lattice(rate_lattice=short_rate_lattice)
price = bond_lattice["t=0"]
print(str(*price) + " or 61.6103 (correct answer) with fewer significant digits in short rate lattice")

# Question 2 compute the price of a forward contract, matures at t = 4,
bb.n = 4
bond_lattice_4 = bb.make_bond_lattice(rate_lattice=short_rate_lattice)
forward_lattice = bb.make_forward_or_future_lattice(bond_lattice=bond_lattice_4,
                                                    rate_lattice=short_rate_lattice,
                                                    is_forward=True)
b_price = bond_lattice["t=0"][0]
f_price = forward_lattice["t=0"][0]
print(str(round(100 * b_price / f_price, 4)) + " or 74.87 (correct answer) with fewer significant digits in short rate lattice")

# Question 3 compute the price of a future contract
forward_lattice = bb.make_forward_or_future_lattice(bond_lattice=bond_lattice,
                                                    rate_lattice=short_rate_lattice,
                                                    is_forward=False)
price = forward_lattice["t=0"]
print(str(*price) + " or 74.81 (correct answer) with fewer significant digits in short rate lattice.")

# Question 4 compute the price of an american call option
bb.n = 6
options_lattice = bb.make_option_lattice(bond_lattice=bond_lattice,
                                         rate_lattice=short_rate_lattice,
                                         is_call=True, is_american=True, strike=80)
price = options_lattice["t=0"]
print(str(*price) + " or 2.35 (correct answer) with fewer significant digits in short rate lattice.")

# The following Questions require about 6 significant digits
# to answer correctly, unlike the previous questions.

# Question 5 compute init value of forward-starting swap, starting at t=1
bb.n=10
swap_lattice = bb.make_swap_lattice(rate_lattice=short_rate_lattice,
                                    term_start=1, #first payment is >t=1
                                    fixed_rate=.045)
price = swap_lattice["t=0"][0]*1000000
print(round(price,0))

# Question 6 compute the init price of a swaption that matures at time
bb.n = 5
swaption_lattice = bb.make_swaption_lattice(swap_lattice=swap_lattice, rate_lattice=short_rate_lattice, strike=0)
price = swaption_lattice["t=0"][0]*1000000
print(round(price,0))
