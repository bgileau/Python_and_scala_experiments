import random
import numpy as np
import pandas as pd
import scipy.stats

import math
import statistics

import matplotlib.pyplot as plt


# General flow:
# Need to specify a Bi sequence. Can use python random perhaps to do this part.

# Experiment with feeding it some garbage, handmade sequence of Bi to check performance.

# Initialize Bi randomly
def initialize_bi(q):
    # q = length of sequence
    bi_list = list(np.random.randint(0,2,q))
    print(sum(bi_list))
    return bi_list


def extend_bi_sequence(bi_list, generate_count, r):
    q = len(bi_list)

    for i in range(len(bi_list), len(bi_list) + generate_count):
        new_val_bi = (bi_list[i - r] + bi_list[i - q]) % 2
        bi_list.append(new_val_bi)

    return bi_list


def convert_bi_to_unif(bi_list, l):

    q = len(bi_list)

    end_range = int(q - q % l)  # allows for a clean division (discards the vals after end_range and before q.)

    unif_list = []

    for l_chunk in range(0, end_range, l):
        l_chunk_sum = 0

        start_slice = l_chunk
        end_slice = l_chunk + l

        bi_list_l_chunk = bi_list[start_slice: end_slice]

        for x in range(0, len(bi_list_l_chunk)):
            # start with the rightmost item (x = 0, with x being the exp power). Add this value to the sum
            # Then, chop off last value from consideration
            if bi_list_l_chunk[-x - 1] == 1:
                l_chunk_sum += (2**x)

        l_chunk_val = l_chunk_sum / 2**l
        unif_list.append(l_chunk_val)

    return unif_list


def chi_sq_gof(k, unif_list):
    df = k - 1

    np_unif_list = np.array(unif_list)
    category_counts_dict = {.1: 0, .2: 0, .3: 0, .4: 0, .5: 0, .6: 0, .7: 0, .8: 0, .9: 0, 1: 0}

    for keys, vals in category_counts_dict.items():
        key_val = keys - .1
        category_counts_dict[keys] = np_unif_list[(np_unif_list < keys) & (np_unif_list > key_val)].size

    chi_sq_TS = 0
    for keys, vals in category_counts_dict.items():
        chi_sq_numerator = (category_counts_dict[keys] - int(len(unif_list) / k)) ** 2
        chi_sq_TS += chi_sq_numerator / int(len(unif_list) / k)


    chi_sq_p_value = 1 - scipy.stats.chi2.cdf(x=chi_sq_TS, df=df)

    return chi_sq_p_value


def runs_up_and_down_test(unif_list):
    # Note: "Run" is a series of similar observations
    runs_up_and_down = []

    # Up and down test
    idx = 0
    for idx in range(0, len(unif_list)):
        current_val = unif_list[idx]

        if idx == 0:
            last_value = current_val
        else:  # handle creating lists of continuous runs here
            if current_val > last_value:
                append_val = "+"
            else:
                append_val = "-"

            last_value = current_val

            runs_up_and_down.append(append_val)

    lists_up_and_down = []

    sub_list_items = []

    for run_idx in range(0, len(runs_up_and_down)):
        if run_idx < len(runs_up_and_down) - 1:

            if run_idx == 0:
                sub_list_items.append(runs_up_and_down[run_idx])
            else:
                if runs_up_and_down[run_idx] == runs_up_and_down[run_idx - 1]:
                    sub_list_items.append(runs_up_and_down[run_idx])
                else:
                    # append what we have
                    lists_up_and_down.append(sub_list_items)
                    # clear it
                    sub_list_items = []

                    sub_list_items.append(runs_up_and_down[run_idx])
        else:
            lists_up_and_down.append(sub_list_items)
            break

    #print(lists_up_and_down)

    A = len(lists_up_and_down)
    n = len(runs_up_and_down)

    EA = ((2 * n) - 1) / 3
    VarA = ((16 * n) - 29) / 90
    up_and_down_test_stat = abs((A - EA) / (VarA ** 1 / 2))

    up_and_down_z_score = scipy.stats.norm.cdf(up_and_down_test_stat)
    up_and_down_p_value = scipy.stats.norm.sf(abs(up_and_down_z_score)) * 2

    return up_and_down_p_value


def above_and_below_test(unif_list):
    # Note: "Run" is a series of similar observations
    runs_above_and_below = []

    n1 = 0
    n2 = 0
    n = len(unif_list)

    runs_mean = np.array(unif_list).sum() / n

    #print(runs_mean)



    # Up and down test
    for idx in range(0, len(unif_list)):
        current_val = unif_list[idx]

        if current_val < runs_mean:
            append_val = "-"
            n2 += 1
        else:
            append_val = "+"
            n1 += 1

        runs_above_and_below.append(append_val)

    lists_above_and_below = []

    sub_list_items = []

    for run_idx in range(0, len(runs_above_and_below)):
        if run_idx < len(runs_above_and_below) - 1:

            if run_idx == 0:
                sub_list_items.append(runs_above_and_below[run_idx])
            else:
                if runs_above_and_below[run_idx] == runs_above_and_below[run_idx - 1]:
                    sub_list_items.append(runs_above_and_below[run_idx])
                else:
                    # append what we have
                    lists_above_and_below.append(sub_list_items)
                    # clear it
                    sub_list_items = []

                    sub_list_items.append(runs_above_and_below[run_idx])
        else:
            lists_above_and_below.append(sub_list_items)
            break

    #print(lists_above_and_below)

    B = len(lists_above_and_below)
    n = len(lists_above_and_below)
    EB = ((2 * n1 * n2)/n) + .5
    VarB_num = 2*n1*n2 * (2*n1*n2 - n)
    VarB_denom = (n ** 2) * (n-1)
    VarB = VarB_num / VarB_denom
    above_and_below_test_stat = abs((B - EB) / (VarB ** 1 / 2))

    above_and_below_z_score = scipy.stats.norm.cdf(above_and_below_test_stat)
    above_and_below_p_value = scipy.stats.norm.sf(abs(above_and_below_z_score)) * 2

    #print("above/below z score", above_and_below_z_score)

    return above_and_below_p_value


def correlation_test(unif_list):
    n = len(unif_list)

    summation_val = 0

    for i in range(0, len(unif_list)-1):
        summation_val += (unif_list[i] * unif_list[i+1])

    p_hat = (summation_val * (12/(n-1))) - 3
    var_p_hat = ((13 *n) - 19) / ((n-1) ** 2)

    z0 = p_hat / math.sqrt(var_p_hat)
    correlation_test_p_value = scipy.stats.norm.sf(abs(z0)) * 2

    return correlation_test_p_value


if __name__ == "__main__":

    use_handmade_bi = False

    if use_handmade_bi:
        bi_list = [0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1]
        #bi_list = [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0]
        #bi_list = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

        q = len(bi_list)
        r = int((q/2) * random.random()) + 1
        if q > 8:
            l = 12
        else:
            l = 4

        gen_number = 150
    else:
        q = 20000
        r = int((q/16) * random.random()) + 1
        bi_list = initialize_bi(q)

        l = 16
        gen_number = 5000000

        # final number of uniforms to be expected is (q + gen_number)/L


    new_bi_list = extend_bi_sequence(bi_list, gen_number, r)
    unif_list = convert_bi_to_unif(new_bi_list, l)


    # Perform Statistical tests on PRNs to check if valid
    KS_gof_test_stat, KS_gof_test_p_val = scipy.stats.kstest(np.array(unif_list), "uniform")


    # Chi-SQ test:
    k = 10  # intervals
    alpha = .05

    chi_sq_p_value = chi_sq_gof(k, unif_list)

    # Run tests for independence

    # Up and down test
    up_and_down_p_value = runs_up_and_down_test(unif_list)

    # Above and below the mean
    #print(unif_list[:50])
    above_and_below_p_value = above_and_below_test(unif_list)

    correlation_test_p_value = correlation_test(unif_list)

    print(f"Kolmogorov-Smirnov Test p value: {KS_gof_test_p_val}")
    print(f"Chi-square Test p value: {chi_sq_p_value}")

    print(f"Up and down Test p value: {up_and_down_p_value}")
    print(f"Above and below Test p value: {above_and_below_p_value}")
    print(f"Correlation Test p value: {correlation_test_p_value}")

    #x = range(1, len(unif_list) + 1)
    #y = unif_list



    # Generate normal deviates:

    # Acceptance-Rejection Normal
    # Repeat following until Y <= g(Y)
    # Generate U from U(0,1) - aka. select a uniform from list
    # Generate Y from h(y) - push a random uniform value through formula
    do_ar = True

    if do_ar:
        sample_number = 250000
        X_vals = []

        U_sum = 0
        U_py_sum = 0

        for i in range(0, sample_number):
            U = 99
            Y = 5

            while U > math.exp(-.5 * ((Y - 1) ** 2)):
                U = random.choice(unif_list)
                U_py = random.random()

                # print(U, U_py)

                U_sum += U
                U_py_sum += U_py
                # print(random_val, U)
                Y = random.uniform(-5, 6)

            X_vals.append(Y - 1)

        X_vals_pd = pd.Series(X_vals)

        # print(U_sum, U_py_sum)

        plot6 = plt.figure(6)
        plt.hist(X_vals_pd, bins=100)
        plt.show()

        # Normal Deviate p value (is it normal?)
        print(f"Normal deviate AR p value: {scipy.stats.normaltest(X_vals_pd)[1]}")
        print(f"Normal deviate AR variance: {statistics.variance(X_vals)}, mean: {statistics.mean(X_vals)}")

    # Box-Mueller one normal

    do_bm = True
    if do_bm:
        sample_number = 1000000
        Z_vals = []

        for i in range(0, sample_number):
            U1 = random.choice(unif_list)
            U2 = random.choice(unif_list)

            # Handle the unlikely case where a 0 is generated by the PRN generator
            if U1 == 0 or U2 == 0:
                continue

            Z = math.sqrt(-2 * math.log(U1)) * math.cos(2 * math.pi * U2)

            Z_vals.append(Z)

        Z_vals_pd = pd.Series(Z_vals)

        plot7 = plt.figure(7)
        plt.hist(Z_vals_pd, bins=75)
        plt.show()

        # Normal Deviate p value (is it normal?)
        print(f"Normal deviate BM p value: {scipy.stats.normaltest(Z_vals_pd)[1]}")
        print(f"Normal deviate BM variance: {statistics.variance(Z_vals)}, mean: {statistics.mean(Z_vals)}")

    # Inverse transform
    do_ivt = True

    if do_ivt:
        unif_list_inv_transform_deviates = []

        for uniform_val in range(len(unif_list)):
            unif_list_inv_transform_deviates.append(scipy.stats.norm.ppf(unif_list[uniform_val]))

        unif_list_inv_transform_deviates_pd = pd.Series(unif_list_inv_transform_deviates)

        unif_list_inv_transform_deviates_pd = unif_list_inv_transform_deviates_pd[abs(unif_list_inv_transform_deviates_pd) < 10]

        plot5 = plt.figure(5)
        plt.hist(unif_list_inv_transform_deviates_pd, bins=100)
        plt.show()

        # Normal Deviate p value (is it normal?)
        print(f"Normal deviate IVT p value: {scipy.stats.normaltest(unif_list_inv_transform_deviates_pd)[1]}")
        print(f"Normal deviate IVT variance: {statistics.variance(list(unif_list_inv_transform_deviates_pd))}, mean: {statistics.mean(list(unif_list_inv_transform_deviates_pd))}")

    plot_pts = True

    if plot_pts:
        start_pt = 100000

        # number_of_pts = len(unif_list)
        number_of_pts = 100
        plot1 = plt.figure(1)

        x = range(1 + start_pt, number_of_pts + 1 + start_pt)
        y = unif_list[start_pt:number_of_pts+start_pt]

        plt.scatter(x, y)

        number_of_pts = 1000
        plot2 = plt.figure(2)

        x = range(1 + start_pt, number_of_pts + 1 + start_pt)
        y = unif_list[start_pt:number_of_pts+start_pt]

        plt.scatter(x, y)

        number_of_pts = 3000
        plot3 = plt.figure(3)

        x = range(1 + start_pt, number_of_pts + 1 + start_pt)
        y = unif_list[start_pt:number_of_pts+start_pt]

        plt.scatter(x, y)

        number_of_pts = len(unif_list)
        plot4 = plt.figure(4)

        x = range(1, number_of_pts + 1)
        y = unif_list[:number_of_pts]

        plt.scatter(x, y)

        plt.xlabel('x - axis')
        plt.ylabel('y - axis')
        plt.show()

