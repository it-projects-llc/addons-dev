#!/usr/bin/python
import random
import datetime
import sys
TIMESHEET_NUM = 200
INCOME_NUM = 20
FIRST_DAY = datetime.datetime(2017, 1, 1)
MAX_DAYS = 100


try:
    gen_type = sys.argv[1]
except:
    gen_type = 'lines'


def random_normal(vmin, vmax, avg, sigma):
    value = int(round(abs(random.normalvariate(avg, sigma))))
    return max(vmin, min(vmax, value))


def random_amount(alpha):
    return -random_normal(10, 300, 100, 50)



def rand_sq():
    return random.random() * random.random()


def format_date(day):
    return (FIRST_DAY + datetime.timedelta(days=day)).strftime('%Y-%m-%d')


def random_date(alpha):
    avg = alpha * MAX_DAYS
    day = random_normal(1, MAX_DAYS, avg, 5)
    return format_date(day)


def random_project_task(alpha):
    # 1-4
    avg = round(0.5 + alpha * 4)
    p = random_normal(1, 4, avg, 1)
    # 1-5
    t = round(0.5 + (5 * rand_sq()))
    return 'a%i' % p, 'p%i' % p, 't%i%i' % (p, t)


def random_user():
    return random_normal(1, 4, 2.5, 1.5)


def lines():
    print 'id,name,amount,date,account_id/id,task_id/id,project_id/id,user_id/id'

    # timesheet expenses
    for i in range(1, TIMESHEET_NUM+1):
        alpha = i / TIMESHEET_NUM
        amount = random_amount(alpha)
        date = random_date(alpha)
        a, p, t = random_project_task(alpha)
        u = random_user()
        print 'line{i},name{i},{amount},{date},{a},{t},{p},u{u}'.format(
            i=i, amount=amount, date=date, a=a, p=p, t=t, u=u
        )

    # periodic payments
    PERIODIC_PAYMENTS = [
        ('ae1', 0, -2900),
        ('ae2', 7, -3800),
        ('ae3', 7, -6800),
        ('ae4', 5, -300),
    ]
    for analytic, delta, amount in PERIODIC_PAYMENTS:
        for i in range(3):
            date = format_date(delta + i*30)
            print 'line_periodic_expense_{a}_{i},name{i},{amount},{date},{a},,,'.format(
                i=i, amount=amount, date=date, a=a,
            )

    # income
    for i in range(1, INCOME_NUM+1):
        p_id = round(0.5 + (4 * random.random()))
        a = 'a%i' % p_id
        p = 'p%i' % p_id
        amount = random_normal(10, 20333, 4000, 2000)
        date = format_date(round(MAX_DAYS * i / INCOME_NUM))
        print 'line_income_{i},name{i},{amount},{date},{a},,{p},'.format(
            i=i, amount=amount, date=date, a=a, p=p, t='', u=''
        )



def links():
    pass


if __name__ == "__main__":
    if gen_type == 'links':
        links()
    else:
        lines()
