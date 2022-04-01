#include <unistd.h>

int main(int argc, char **argv) {
    int delay = atoi(argv[1]);
    sleep(delay);
}
