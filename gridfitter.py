#!/usr/bin/python3
# Copyright © 2017 Po Huit
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Add powergrid upgrades to an EVE Online hull.

power_grid_management_level = 5
energy_grid_upgrades_level = 5
capacitor_management_level = 5
grid_start=83.75
grid_needed = 153.0

LOW=0
RIG=1
PDS=2

class Bonus(object):
    # XXX Needs order variable to sort.
    # order = 0

    def apply(self, grid):
        panic("internal error: bonus base apply")

class Increase(Bonus):
    order = 1

    def __init__(self, increase):
        self.increase = increase * (1.0 + power_grid_management_level * 0.05)

    def apply(self, grid):
        return self.increase + grid

class Percent(Bonus):
    order = 2

    def __init__(self, percent):
        self.mult = 1.0 + percent / 100.0

    def apply(self, grid):
        return self.mult * grid

class Module(object):
    def __init__(self, name, bonus, cost, category=LOW, enable=True):
        self.name = name
        self.bonus = bonus
        self.cost = cost
        self.category = category
        self.enable = enable
    
modules = [
    Module("Micro Auxiliary Power Core I", Increase(10), 200),
    Module("Vigor Compact Micro Auxiliary Power Core", Increase(11), 13_500),
    Module("Micro Auxiliary Power Core II", Increase(12), 1_080,
           enable=(capacitor_management_level == 5)),
    Module("Navy Micro Auxiliary Power Core", Increase(13), 7_900),
    Module("Thukker Micro Auxiliary Power Core", Increase(12), 55_000),
    Module("Reactor Control Unit I", Percent(10), 6),
    Module("Mark I Compact Reactor Control Unit", Percent(12), 37),
    Module("Reactor Control Unit II", Percent(15), 592,
           enable=(energy_grid_upgrades_level == 5)),
    Module("Dark Blood Reactor Control Unit", Percent(15.5), 8_880),
    Module("Brokara's Modified Reactor Control Unit", Percent(16.27), 500_000),
    Module("Chelm's Modified Reactor Control Unit", Percent(18.6), 1_000_000),
    Module("Small Ancillary Current Router I", Percent(10), 550,
           category=RIG),
    Module("Small Ancillary Current Router II", Percent(15), 4_100,
           category=RIG),
    Module("Power Diagnostic System I", Percent(5), 8.75,
           category=PDS),
    Module("Mark I Compact Power Diagnostic System", Percent(5.5), 40,
           category=PDS),
    Module("Power Diagnostic System II", Percent(6), 1160,
           category=PDS, enable=(energy_grid_upgrades_level == 4)),
]
modules = sorted(modules, key=(lambda m: m.bonus.order))

def fit_modules(to_fit, counts, grid):
    for c in counts:
        if c < 0:
            return None
    if grid >= grid_needed:
        return grid, 0, []
    if len(to_fit) == 0 or counts == (0,) * len(counts):
        return None
    m = to_fit.pop(0)
    if not m.enable:
        return fit_modules(list(to_fit), counts, grid)

    ngrid = grid
    best_grid = None
    min_cost = None
    best_fit = None
    for i in range(counts[m.category] + 1):
        ncounts = list(counts)
        ncounts[m.category] -= i
        if ncounts[m.category] < 0:
            break
        rest = fit_modules(list(to_fit), tuple(ncounts), ngrid)
        ngrid = m.bonus.apply(ngrid)
        if rest == None:
            continue
        cgrid, ccost, cfit = rest
        ccost += m.cost * i
        if min_cost == None or ccost < min_cost:
            min_cost = ccost
            best_grid = cgrid
            best_fit = [m.name] * i + cfit
    if best_fit == None:
        return None
    return best_grid, min_cost, best_fit

print(fit_modules(modules, (1, 3, 2), grid_start))
