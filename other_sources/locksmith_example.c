#include <pthread.h>

pthread_mutex_t lock1, lock2;

int count1 = 0, count2 = 0;

void atomic_inc(pthread_mutex_t *lock, int *count)
{
    pthread_mutex_lock(lock);
    *count++;
    pthread_mutex_unlock(lock);
}

void *thread1(void *a)
{
    int *y = (int*)a; /* int* always */
    while(1)
    {
        *y++; /* thread−local */
    }
}

void *thread2(void *c)
{
    while(1)
    {
        pthread_mutex_lock(&lock1);
        count1++;
        pthread_mutex_unlock(&lock1);
        count2++; /* access without lock */
    }
}

void *thread3(void *b)
{
    while(1)
    {
        /* needs polymorphism for atomic inc */
        atomic_inc(&lock1, &count1);
        atomic_inc(&lock2, &count2);
    }
}


int main(void)
{
    pthread_t t1, t2, t3;
    int local = 0;

    pthread_mutex_init(&lock1, NULL);
    pthread_mutex_init(&lock2, NULL);

    local++;

    pthread_create(&t1, NULL, thread1, &local);
    pthread_create(&t2, NULL, thread2, NULL);
    pthread_create(&t3, NULL, thread3, NULL);
}
