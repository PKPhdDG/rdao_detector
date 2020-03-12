#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int add(int n, ...)
{
    /* Define temporary variables */
    va_list list;
    int total = 0;

    /* Set where the variable length part of the argument list ends */
    va_start(list, n);

    /* Loop through each argument adding the int values */
    for (int i=0; i < n; i++)
        total = total + va_arg(list, int);

    /* Clean up */
    va_end(list);

    /* Return the calculated total */
    return total;
}

void *thread_test(void *arguments)
{
    int result = add(5, 1, 2, 3, 4, 5);
    printf("Result: %d", result);

    return (void*)NULL;
}

int main(int argc, char *argv[])
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
