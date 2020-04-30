#include <stdio.h>

static volatile long long result;

int sum(int n);

int main() {
    int number;

    printf("Enter a positive integer: ");
    scanf("%d", &number);
    result = sum(number);
    printf("Sum = %lld", result);
    return 0;
}

int sum(int n) {
    if (n == 0)
        return n;
    else
        return n + sum(n-1);
}
