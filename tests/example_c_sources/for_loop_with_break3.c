#include <stdio.h>

int main()
{
    for (int i=0; i < 100; ++i)
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
