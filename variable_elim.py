"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

Class for the implementation of the variable elimination algorithm.

"""
import itertools
import pandas as pd


def reduce_factors(factors, observed_values):
    """
    Reduce factors based on the observed values
    """
    # Loop through all factors
    for key in factors:
        # Check through all observed variables if they are in factor
        for variable, value in observed_values.items():
            if variable in key[1]:
                # Take current factor we are checking
                current_factor_df = factors[key]
                # Check in the factor where we need to change observed variable value
                mismatched_indices = current_factor_df.index[current_factor_df[variable] != value]
                # Delete values from factor that don't match the observation
                current_factor_df.drop(mismatched_indices, inplace=True)


def multiply_factor(variable, first_factor, second_factor):
    """
    Multiply two factors based on the variable
    """
    merged_factors = pd.merge(first_factor, second_factor, on=variable)
    merged_factors['prob'] = merged_factors['prob_x'] * merged_factors['prob_y']
    merged_factors.drop(columns=['prob_x', 'prob_y'], inplace=True)
    return merged_factors


def marginalize(variable, factor_for_sum):
    """
    Marginalize the factor based on the variable
    """
    vars_to_keep = [col for col in factor_for_sum.columns if col != variable and col != 'prob']
    if len(vars_to_keep) > 0:
        factor_for_sum = factor_for_sum.groupby(vars_to_keep)['prob'].sum().reset_index()
    return vars_to_keep, factor_for_sum


class VariableElimination:
    def __init__(self, network):
        """
        Initialize the variable elimination algorithm with the specified network.
        Add more initializations if necessary.
        """
        self.factors = network.probabilities
        self.observed = {}
        self.max_size_factor = 0

    def run(self, query, observed, elim_order):
        """
        Use the variable elimination algorithm to find out the probability
        distribution of the query variable given the observed variables

        Input:
            query:      The query variable
            observed:   A dictionary of the observed variables {variable: value}
            elim_order: Either a list specifying the elimination ordering
                        or a function that will determine an elimination ordering
                        given the network during the run

        Output: A variable holding the probability distribution
                for the query variable
        """
        var = 0
        i = len(self.factors)
        self.initialize_factors(observed)
        # Loop through all variables in the elimination order
        for variable in elim_order:
            print("Eliminating variable", variable)
            contains = 0
            factors_containing_variable = []
            # Check which factors contain variable
            for factor in self.factors:
                if variable in factor[1]:
                    contains += 1
                    factors_containing_variable.append(factor)
            # If there are multiple factors containing the variable, multiply them
            if contains > 1:
                print("Multiplying factors: \n", factors_containing_variable)
                print("Factors before multiplication:")
                for factor in factors_containing_variable:
                    print(self.factors[factor])
                variables, factor_for_sum = self.multiply_all_variable_factors(variable, factors_containing_variable)
                print("Multiplied factor result: \n", factor_for_sum)
                print()

                print("Summing out factor with variable: \n", variable)
                print("Factor before summation: \n", factor_for_sum)
                for i in range(0, len(factors_containing_variable)):
                    self.factors.pop(factors_containing_variable[i])
            # If there is only one factor containing the variable, sum out the variable
            else:
                print("No multiplication needed for variable: \n", variable)
                print("Summing out factor with variable: \n", variable)
                factor_for_sum = self.factors[factors_containing_variable[0]]
                print("Factor before summation: \n", self.factors[factors_containing_variable[0]])
                self.factors.pop(factors_containing_variable[0])

            # Sum out the variable
            variables, summed_out_fac = marginalize(variable, factor_for_sum)
            print("Result of the summation: \n", summed_out_fac)

            self.factors[i, tuple(variables)] = summed_out_fac
            i += 1
            print("Adding new factor to the factors: \n", summed_out_fac)
            print()
            print()

        lastindex = i
        # If there are multiple factors containing the query variable, multiply them
        if len(self.factors) > 1:
            factors_containing_variable = []
            for fact in self.factors:
                factors_containing_variable.append(fact)

            print("Last factors with query variable, before multiplication: ", self.factors)
            result = self.multiply_all_variable_factors(query, factors_containing_variable)

            for i in range(0, len(factors_containing_variable)):
                self.factors.pop(factors_containing_variable[i])

            factor = result[1]
            self.factors[lastindex, tuple([query, ])] = result
        # If there is only one factor containing the query variable, then continue
        else:
            factor = summed_out_fac

        # Normalize the factor
        print("Final factor before normalization: \n", factor)
        prob_sum = factor['prob'].sum()
        factor['prob'] = factor['prob'] / prob_sum
        print("Resulting probability distribution after variable elimination: \n", factor)

    def multiply_all_variable_factors(self, variable, factors_containing_variable):
        """
        Multiply all factors containing the variable
        """
        vars = []
        for key in factors_containing_variable:
            vars.extend(list(self.factors[key].columns[:-1]))
            vars = list(set(vars))
        first_factor = self.factors[factors_containing_variable[0]]

        for i in range(1, len(factors_containing_variable)):
            factor_mul_result = multiply_factor(variable, first_factor,
                                                self.factors[factors_containing_variable[i]])
            first_factor = factor_mul_result
        return vars, factor_mul_result

    def initialize_factors(self, observed_values):
        """
        Initialize factors based on the observed values
        """
        factors_copy = {}
        for key, factor in self.factors.items():
            factors_copy[key] = factor.copy()
        new_factors = {}
        # Reassign keys with indices and involved variables
        index = 0
        for key, factor in factors_copy.items():
            # Take all column names, except for 'prob' column
            new_key = (index, tuple(factor.columns[:-1]))
            new_factors[new_key] = factor
            index += 1
        # Reduce factors given the observation
        print(type(new_factors))
        reduce_factors(new_factors, observed_values)
        # Change factors in the variable elimination class
        self.factors = new_factors
