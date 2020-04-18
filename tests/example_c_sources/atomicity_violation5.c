#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

volatile int account_balance1 = 0, account_balance2 = 10;
pthread_mutex_t m;

void* deposit(void *args) {

    for (int i=0; i<10; i++)
    {
        pthread_mutex_lock(&m);
        ++account_balance1;
        --account_balance2;
        pthread_mutex_unlock(&m);

        usleep(100);
    }

    pthread_mutex_lock(&m);
    printf("Account balance1: %d\n", account_balance1);
    printf("Account balance2: %d\n", account_balance2);
    pthread_mutex_unlock(&m);
    return NULL;
}

void *display_account_info(void *args)
{
    printf("Account Balance1: %d\n", account_balance1);
    printf("Account Balance2: %d\n", account_balance2);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    printf("App start work with account balance1 = %d\n", account_balance1);
    printf("App start work with account balance2 = %d\n", account_balance2);

    pthread_create(&t1, NULL, deposit, NULL);
    pthread_create(&t2, NULL, display_account_info, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("App finish work with account balance1 = %d\n", account_balance1);
    printf("App finish work with account balance2 = %d\n", account_balance2);
    return 0;
}
