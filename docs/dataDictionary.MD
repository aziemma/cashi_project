# Data Dictionary

## Loan Details

| Column | Description |
|--------|-------------|
| `loan_amnt` | Loan amount requested |
| `term` | Loan term (36 or 60 months) |
| `int_rate` | Interest rate (%) |
| `installment` | Monthly payment amount |
| `grade` | Lending Club assigned grade (A-G, A=best) |
| `purpose` | Reason for loan (debt_consolidation, credit_card, etc.) |
| `issue_d` | Month loan was issued |
| `initial_list_status` | Loan listing type (whole/fractional) |
| `disbursement_method` | How funds were sent (Cash/DirectPay) |

## Borrower Profile

| Column | Description |
|--------|-------------|
| `annual_inc` | Self-reported annual income |
| `emp_length` | Employment length (< 1 year to 10+ years) |
| `emp_length_numeric` | Numeric version (0.5 to 10) |
| `home_ownership` | RENT, OWN, MORTGAGE, OTHER |
| `verification_status` | Income verified, source verified, or not |
| `addr_state` | Borrower's state |
| `application_type` | Individual or joint application |
| `dti` | Debt-to-income ratio (monthly debt / income × 100) |

## Credit History

| Column | Description |
|--------|-------------|
| `earliest_cr_line` | Date of first credit account |
| `credit_history_months` | Months since first credit line |
| `delinq_2yrs` | Delinquencies in past 2 years |
| `inq_last_6mths` | Credit inquiries in past 6 months |
| `inq_last_12m` | Credit inquiries in past 12 months |
| `inq_fi` | Inquiries from finance companies |
| `pub_rec` | Public records (liens, judgments) |
| `pub_rec_bankruptcies` | Number of bankruptcies |
| `collections_12_mths_ex_med` | Collections (excl. medical) in 12 months |
| `chargeoff_within_12_mths` | Charge-offs in past 12 months |
| `acc_now_delinq` | Accounts currently delinquent |
| `delinq_amnt` | Amount currently delinquent |
| `tot_coll_amt` | Total collection amounts ever |

## Credit Accounts

| Column | Description |
|--------|-------------|
| `open_acc` | Open credit accounts |
| `total_acc` | Total credit accounts ever |
| `num_sats` | Satisfactory accounts |
| `acc_open_past_24mths` | Accounts opened in past 24 months |
| `pct_tl_nvr_dlq` | % of accounts never delinquent |
| `num_accts_ever_120_pd` | Accounts ever 120+ days past due |
| `num_tl_90g_dpd_24m` | Accounts 90+ days past due in 24 months |
| `num_tl_op_past_12m` | Accounts opened in past 12 months |

## Revolving Credit (Credit Cards)

| Column | Description |
|--------|-------------|
| `revol_bal` | Total revolving balance |
| `revol_util` | Revolving utilization (%) |
| `total_rev_hi_lim` | Total revolving credit limit |
| `bc_util` | Bank card utilization (%) |
| `bc_open_to_buy` | Available credit on bank cards |
| `max_bal_bc` | Max balance on bank cards |
| `total_bc_limit` | Total bank card credit limit |
| `percent_bc_gt_75` | % of bank cards with >75% utilization |
| `num_bc_tl` | Number of bank card accounts |
| `num_bc_sats` | Satisfactory bank card accounts |
| `num_actv_bc_tl` | Active bank card accounts |
| `num_rev_accts` | Number of revolving accounts |
| `num_actv_rev_tl` | Active revolving accounts |
| `num_op_rev_tl` | Open revolving accounts |
| `num_rev_tl_bal_gt_0` | Revolving accounts with balance > 0 |
| `open_rv_12m` | Revolving accounts opened in 12 months |
| `open_rv_24m` | Revolving accounts opened in 24 months |
| `all_util` | Overall utilization (%) |
| `mo_sin_old_rev_tl_op` | Months since oldest revolving account |
| `mo_sin_rcnt_rev_tl_op` | Months since newest revolving account |
| `mths_since_recent_bc` | Months since newest bank card |

## Installment Loans (Auto, Personal)

| Column | Description |
|--------|-------------|
| `total_bal_il` | Total installment loan balance |
| `total_il_high_credit_limit` | Total installment high credit limit |
| `il_util` | Installment loan utilization (%) |
| `num_il_tl` | Number of installment accounts |
| `open_il_12m` | Installment accounts opened in 12 months |
| `open_il_24m` | Installment accounts opened in 24 months |
| `open_act_il` | Active installment accounts |
| `mths_since_rcnt_il` | Months since newest installment account |
| `mo_sin_old_il_acct` | Months since oldest installment account |
| `open_acc_6m` | Accounts opened in past 6 months |

## Balances & Limits

| Column | Description |
|--------|-------------|
| `tot_cur_bal` | Total current balance (all accounts) |
| `avg_cur_bal` | Average current balance |
| `tot_hi_cred_lim` | Total high credit limit |
| `total_bal_ex_mort` | Total balance excluding mortgage |
| `total_cu_tl` | Total credit union tradelines |
| `mort_acc` | Number of mortgage accounts |
| `mo_sin_rcnt_tl` | Months since most recent account |
| `mths_since_recent_inq` | Months since most recent inquiry |

## Target

| Column | Description |
|--------|-------------|
| `loan_status` | Original status (Fully Paid, Charged Off, etc.) |
| `default` | Binary target: 1 = default, 0 = good |
