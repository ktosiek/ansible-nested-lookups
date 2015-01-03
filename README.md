[![Build Status](https://travis-ci.org/ktosiek/ansible-nested-lookups.svg?branch=master)](https://travis-ci.org/ktosiek/ansible-nested-lookups)
[![Coverage Status](https://coveralls.io/repos/ktosiek/ansible-nested-lookups/badge.png?branch=master)](https://coveralls.io/r/ktosiek/ansible-nested-lookups?branch=master)


This plugin allows users to apply multiple lookups/transformations to data before using it in loop.

Example
=======

    - name: Add IPs of all hosts in specified groups to a file
      lineinfile:
        dest: /ips
        line: '{{ item }}'
      with_multiple:
        # First step: get a flat list of all hosts
        - with_flattened: [groups.first_group, groups.second_group]
        # Second step: for each item from previous step, get the ipv4 address
        - apply: hostvars[item].ansible_default_ipv4.address

    - name: Same, but with multiple addresses
        - with_flattened: [groups.all]
        - apply: hostvars[item].ansible_all_ipv4_addresses + hostvars[item].ansible_all_ipv6_addresses
        - with_flattened: items


Usage
=====

A step in with_multiple might be:

* `raw list/string`: it will be templated without any fancy variables. Good as a first step.
* `with_LOOKUP: ARG`: the specified lookup will get called with ARG as an argument, and with results of previous step in `items` variable
* `apply: TEMPLATE`: each item from previous results will be replaced with rendered TEMPLATE. Value of the item being replaced is available as `item`.

Additionaly, all steps can have `register: some_name` parameter, which will save the result of that step under both `items` and `some_name`.
