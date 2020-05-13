#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

volatile int account_balance = 0, interest_rate = 0;
pthread_mutex_t m, n;

void display_account_info()
{
    printf("Account Balance: %d\n", account_balance);
    printf("Actual interest rate: %d\n", interest_rate);
}

void* deposit(void *args) {

    for (int i=0; i<10; i++)
    {
        pthread_mutex_lock(&m);
        ++account_balance;
        pthread_mutex_unlock(&m);
        usleep(100);
        pthread_mutex_lock(&m);
        pthread_mutex_lock(&n);
        display_account_info();
        pthread_mutex_unlock(&n);
        pthread_mutex_unlock(&m);
    }
    return NULL;
}

void* change_interest(void *args) {
    pthread_mutex_lock(&n);
    interest_rate = 5;
    display_account_info();
    pthread_mutex_unlock(&n);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    printf("App start work with account_balance = %d\n", account_balance);

    pthread_create(&t1, NULL, deposit, NULL);
    pthread_create(&t2, NULL, change_interest, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("App finish work with account_balance = %d\n", account_balance);
    return 0;
}
