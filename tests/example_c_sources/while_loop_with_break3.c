#include <stdio.h>

int main()
{
    int i=0;
    while (i++ < 100)
    {
        if (i < 99) {
            printf("%d\n", i);
        }
        else {
            break;
        }
    }

    return 0;
}
