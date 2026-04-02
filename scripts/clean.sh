#!/bin/bash

echo "[*] Cleaning generated files..."

rm -rf payloads/output/*
rm -rf models/saved/*.pkl
rm -rf logs/*.log

echo "[+] Clean complete"
