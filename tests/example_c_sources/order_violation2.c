#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

pthread_mutex_t m;

void* create_account(void *args) {
    pthread_mutex_lock(&m);
    int **account = (int**)args;
    *account = (int*)malloc(sizeof(int));
    **account = 0;
    printf("Account created. Current balance: %d\r\n", **account);
    pthread_mutex_unlock(&m);
    return NULL;
}

void* deposit(void *args) {
    int *account = (int*)args;
    pthread_mutex_lock(&m);
    for (int i=0; i<1000000; i++)
    {
        ++*account;
    }
    pthread_mutex_unlock(&m);
    return NULL;
}

void* delete_account(void *args) {
    pthread_mutex_lock(&m);
    int **account = (int**)args;
    printf("App finish work with account balance = %d\r\n", **account);
    free(*account);
    pthread_mutex_unlock(&m);
    return NULL;
}

int main() {
    pthread_t t1, t2, t3;
    int *account;
    pthread_create(&t1, NULL, create_account, (void*)&account);
    pthread_create(&t2, NULL, deposit, (void*)account);
    pthread_create(&t3, NULL, delete_account, (void*)&account);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    return 0;
}
