#!/bin/bash
# Unchanged requirements
rm -f unchanged.txt.lock
orb -f -r unchanged.txt
rm -f referred_constraints_unchanged.txt.lock
orb -f -r referred_constraints_unchanged.txt
rm -f referred_requirements_unchanged.txt.lock
orb -f -r referred_requirements_unchanged.txt

# Changed requirements
sed -i s/^setuptools.*/setuptools==83.0.0/g changed.txt
rm -f changed.txt.lock
orb -f -r changed.txt
rm -f referred_constraints_changed.txt.lock
orb -f -r referred_constraints_changed.txt
mv referred_constraints_changed.txt.lock referred_constraints_changed.txt.lock.original
rm -f referred_requirements_changed.txt.lock
orb -f -r referred_requirements_changed.txt
mv referred_requirements_changed.txt.lock referred_requirements_changed.txt.lock.original

sed -i s/^setuptools.*/setuptools==84.0.0/g changed.txt
orb -f -r referred_constraints_changed.txt
mv referred_constraints_changed.txt.lock referred_constraints_changed.txt.lock.actual
mv referred_constraints_changed.txt.lock.original referred_constraints_changed.txt.lock
orb -f -r referred_requirements_changed.txt
mv referred_requirements_changed.txt.lock referred_requirements_changed.txt.lock.actual
mv referred_requirements_changed.txt.lock.original referred_requirements_changed.txt.lock
