/*
 * (c) 2022, Alexei Znamensky <russoz@gmail.com>
 * GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
 */

#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    int delay = atoi(argv[1]);
    sleep(delay);
}
