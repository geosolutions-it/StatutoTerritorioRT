#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


#########################
# PREDEFINED PREDICATES #
# #######################

# always_allow(), always_true()
#     Always returns True.
# always_deny(), always_false()
#     Always returns False.
# is_authenticated(user)
#     Returns the result of calling user.is_authenticated(). Returns False if the given user does not have an is_authenticated method.
# is_superuser(user)
#     Returns the result of calling user.is_superuser. Returns False if the given user does not have an is_superuser property.
# is_staff(user)
#     Returns the result of calling user.is_staff. Returns False if the given user does not have an is_staff property.
# is_active(user)
#     Returns the result of calling user.is_active. Returns False if the given user does not have an is_active property.
# is_group_member(*groups)
#     Factory that creates a new predicate that returns True if the given user is a member of all the given groups, False otherwise.

#############
# SHORTCUTS #
#############

# Managing the shared rule set #
################################
# add_rule(name, predicate)
#     Adds a rule to the shared rule set. See RuleSet.add_rule.
# set_rule(name, predicate)
#     Set the rule with the given name from the shared rule set. See RuleSet.set_rule.
# remove_rule(name)
#     Remove a rule from the shared rule set. See RuleSet.remove_rule.
# rule_exists(name)
#     Returns whether a rule exists in the shared rule set. See RuleSet.rule_exists.
# test_rule(name, obj=None, target=None)
#     Tests the rule with the given name. See RuleSet.test_rule.

# Managing the permissions rule set #
#####################################
# add_perm(name, predicate)
#     Adds a rule to the permissions rule set. See RuleSet.add_rule.
# set_perm(name, predicate)
#     Replace a rule from the permissions rule set. See RuleSet.set_rule.
# remove_perm(name)
#     Remove a rule from the permissions rule set. See RuleSet.remove_rule.
# perm_exists(name)
#     Returns whether a rule exists in the permissions rule set. See RuleSet.rule_exists.
# has_perm(name, user=None, obj=None)
#     Tests the rule with the given name. See RuleSet.test_rule.



