#include <stdio.h>

static volatile long long result;

int sum(int n);
int logN(int n);

int main() {
    int number;

    printf("Enter a positive integer: ");
    scanf("%d", &number);
    result = logN(number);
    printf("Sum = %d", result);
    return 0;
}

int sum(int n) {
    if (n == 0)
        return n;
    else
        return n + logN(n-1);
}

int logN(int n)
{
    printf("Step: %d\n", n);
    return sum(n);
}
