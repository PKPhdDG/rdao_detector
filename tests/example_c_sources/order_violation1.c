#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void* create_account(void *args) {
    int **account = (int**)args;
    *account = (int*)malloc(sizeof(int));
    **account = 0;
    printf("Account created. Current balance: %d\r\n", **account);
}

void* deposit(void *args) {
    int *account = (int*)args;
    for (int i=0; i<1000000; i++)
    {
        ++*account;
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    int *account;
    pthread_create(&t1, NULL, create_account, (void*)&account);
    pthread_create(&t2, NULL, deposit, (void*)account);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("App finish work with account balance = %d\r\n", *account);
    free(account);
    return 0;
}
