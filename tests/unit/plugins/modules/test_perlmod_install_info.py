# Copyright (c) 2023, Jonathan Kamens <jik@kamens.us>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from itertools import chain, permutations
import tempfile
import pytest

from .FakeAnsibleModule import FakeAnsibleModule
from ansible_collections.community.general.plugins.modules.perlmod_install_info import (
    check_installed, dnf_or_yum, apt, cpanm, find_modules
)

perl_V_output = """\
...A whole bunch of output we don't care about...
  @INC:
    /etc/perl
    /usr/local/lib/x86_64-linux-gnu/perl/5.36.0
    /usr/local/share/perl/5.36.0
    /usr/lib/x86_64-linux-gnu/perl5/5.36
    /usr/share/perl5
    /usr/lib/x86_64-linux-gnu/perl-base
    /usr/lib/x86_64-linux-gnu/perl/5.36
    /usr/share/perl/5.36
    /usr/local/lib/site_perl
"""

dnf_net_dns_output = """\
enabling baseos-debuginfo repository
perl-Net-DNS-1.29-4.el9.noarch : DNS resolver modules for Perl
Repo        : appstream
Matched from:
Provide    : perl(Net::DNS) = 1.29

perl-Net-DNS-1.29-6.el9.noarch : DNS resolver modules for Perl
Repo        : appstream
Matched from:
Provide    : perl(Net::DNS) = 1.29
"""

dnf_error_stdout = """\
enabling baseos-debuginfo repository
"""

dnf_error_stderr = """\
Error: No matches found. If searching for a file, try specifying the full path or using a wildcard prefix ("*/") at the beginning.
"""

apt_search_www_mechanize_output = """\
libtest-www-mechanize-perl: /usr/share/perl5/Test/WWW/Mechanize.pm
libwww-mechanize-perl: /usr/share/perl5/WWW/Mechanize.pm
"""

cpanm_test_memory_cycle_output = """\
--> Working on Test::Memory::Cycle
Fetching http://www.cpan.org/authors/id/P/PE/PETDANCE/Test-Memory-Cycle-1.06.tar.gz ... OK
Configuring Test-Memory-Cycle-1.06 ... OK
==> Found dependencies: PadWalker, Devel::Cycle
--> Working on PadWalker
Fetching http://www.cpan.org/authors/id/R/RO/ROBIN/PadWalker-2.5.tar.gz ... OK
Configuring PadWalker-2.5 ... OK
--> Working on Devel::Cycle
Fetching http://www.cpan.org/authors/id/L/LD/LDS/Devel-Cycle-1.12.tar.gz ... OK
Configuring Devel-Cycle-1.12 ... OK
Test-Memory-Cycle-1.06
\\_ PadWalker-2.5
\\_ Devel-Cycle-1.12
"""

cpanm_no_such_module_output = """\
! Finding No::Such::Module on cpanmetadb failed.
! Finding No::Such::Module () on mirror http://www.cpan.org failed.
! Couldn't find module or a distribution No::Such::Module
"""


def make_perl_e_negative_output(perlmod):
    return ("Can't locate %s.pm in @INC (you may need to install the %s "
            "perlmod) (@INC contains: /etc/perl /usr/local/lib/"
            "x86_64-linux-gnu/perl/5.36.0 /usr/local/share/perl/5.36.0 /usr/"
            "lib/x86_64-linux-gnu/perl5/5.36 /usr/share/perl5 /usr/lib/"
            "x86_64-linux-gnu/perl-base /usr/lib/x86_64-linux-gnu/perl/5.36 "
            "/usr/share/perl/5.36 /usr/local/lib/site_perl) at -e line 1.\n"
            "BEGIN failed--compilation aborted at -e line 1.\n") % (
                (perlmod.replace("::", "/"), perlmod))


def test_check_installed_yes():
    amodule = FakeAnsibleModule()
    amodule.register_command(("perl", "-e", "use POSIX"))
    assert check_installed(amodule, "POSIX")


def test_check_installed_no():
    amodule = FakeAnsibleModule()
    amodule.register_command(
        ("perl", "-e", "use No::Such::Module"), rc=2,
        stderr=make_perl_e_negative_output("No::Such::Module"))
    assert not check_installed(amodule, "No::Such::Module")


@pytest.mark.parametrize("cmd", ["dnf", "yum"])
def test_dnf_or_yum_yes(cmd):
    amodule = FakeAnsibleModule()
    amodule.register_command((cmd, "whatprovides", "perl(Net::DNS)"),
                             stdout=dnf_net_dns_output)
    found, packages = dnf_or_yum(amodule, cmd, False, ("Net::DNS",))
    assert found == set(("Net::DNS",))
    assert packages == set(("perl(Net::DNS)",))


@pytest.mark.parametrize("cmd", ["dnf", "yum"])
def test_dnf_or_yum_no(cmd):
    amodule = FakeAnsibleModule()
    amodule.register_command(
        (cmd, "whatprovides", "perl(No::Such::Module)"), rc=1,
        stdout=dnf_error_stdout, stderr=dnf_error_stderr)
    found, packages = dnf_or_yum(amodule, cmd, False, ("No::Such::Module",))
    assert not found
    assert not packages


@pytest.mark.parametrize("cmd", ["dnf", "yum"])
def test_dnf_or_yum_yes_no(cmd):
    amodule = FakeAnsibleModule()
    amodule.register_command((cmd, "whatprovides", "perl(Net::DNS)",
                              "perl(No::Such::Module)", "perl(POSIX)",
                              "perl(Bogus::Module)"), rc=0, stdout="""\
enabling baseos-debuginfo repository
perl-Net-DNS-1.29-4.el9.noarch : DNS resolver modules for Perl
Repo        : appstream
Matched from:
Provide    : perl(Net::DNS) = 1.29

perl-POSIX-1.94-479.el9.x86_64 : Perl interface to IEEE Std 1003.1
Repo        : appstream
Matched from:
Provide    : perl(POSIX) = 1.94

""", stderr="""\
""")
    found, packages = dnf_or_yum(
        amodule, cmd, False,
        ("Net::DNS", "No::Such::Module", "POSIX", "Bogus::Module"))
    assert found == set(("Net::DNS", "POSIX"))
    assert packages == set(("perl(Net::DNS)", "perl(POSIX)"))


def test_apt_yes():
    amodule = FakeAnsibleModule()
    amodule.register_command(("perl", "-V"), stdout=perl_V_output)
    amodule.register_command(("apt-file", "search", "/WWW/Mechanize.pm"),
                             stdout=apt_search_www_mechanize_output)
    found, packages = apt(amodule, False, ("WWW::Mechanize",))
    assert found == set(("WWW::Mechanize",))
    assert packages == set(("libwww-mechanize-perl",))


def test_apt_no():
    amodule = FakeAnsibleModule()
    amodule.register_command(("perl", "-V"), stdout=perl_V_output)
    amodule.register_command(
        ("apt-file", "search", "/No/Such/Module.pm"), rc=1)
    found, packages = apt(amodule, False, ("No::Such::Module",))
    assert found == set()
    assert packages == set()


def test_apt_yes_no():
    amodule = FakeAnsibleModule()
    amodule.register_command(("perl", "-V"), stdout=perl_V_output)
    amodule.register_command(("apt-file", "search", "/WWW/Mechanize.pm"),
                             stdout=apt_search_www_mechanize_output)
    amodule.register_command(("apt-file", "search", "/No/Such/Module.pm"),
                             rc=1)
    found, packages = apt(amodule, False,
                          ("WWW::Mechanize", "No::Such::Module"))
    assert found == set(("WWW::Mechanize",))
    assert packages == set(("libwww-mechanize-perl",))


def fake_mkdtemp():
    return "/not/a/real/directory"


def test_cpanm_yes(mocker):
    mocker.patch.object(tempfile, "mkdtemp", fake_mkdtemp)
    amodule = FakeAnsibleModule()
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "Test::Memory::Cycle"), rc=0,
        stdout=cpanm_test_memory_cycle_output)
    found, dependencies = cpanm(amodule, ("Test::Memory::Cycle",))
    assert found == set(("Test::Memory::Cycle",))
    assert dependencies == set(("Devel::Cycle", "PadWalker"))


def test_cpanm_no(mocker):
    mocker.patch.object(tempfile, "mkdtemp", fake_mkdtemp)
    amodule = FakeAnsibleModule()
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "No::Such::Module"), rc=1,
        stderr=cpanm_no_such_module_output)
    found, dependencies = cpanm(amodule, ("No::Such::Module",))
    assert found == set()
    assert dependencies == set()


def test_cpanm_yes_no(mocker):
    mocker.patch.object(tempfile, "mkdtemp", fake_mkdtemp)
    amodule = FakeAnsibleModule()
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "Test::Memory::Cycle"), rc=0,
        stdout=cpanm_test_memory_cycle_output)
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "No::Such::Module"), rc=1,
        stderr=cpanm_no_such_module_output)
    found, dependencies = cpanm(amodule,
                                ("Test::Memory::Cycle", "No::Such::Module"))
    assert found == set(("Test::Memory::Cycle",))
    assert dependencies == set(("Devel::Cycle", "PadWalker"))


def test_find_modules(mocker):
    mocker.patch.object(tempfile, "mkdtemp", fake_mkdtemp)
    amodule = FakeAnsibleModule()
    amodule.keep_last_command(True)
    for perlmod in ("Net::DNS", "WWW::Mechanize", "Test::Memory::Cycle",
                    "No::Such::Module", "PadWalker"):
        amodule.register_command(
            ("perl", "-e", "use %s" % (perlmod,)), rc=2,
            stderr=make_perl_e_negative_output(perlmod))
    amodule.register_command(("perl", "-e", "use POSIX"))
    amodule.register_command(("perl", "-e", "use Devel::Cycle"))
    # Alas, we don't know what order the arguments will be specified in.
    for order in permutations((
            "perl(No::Such::Module)", "perl(Net::DNS)", "perl(WWW::Mechanize)",
            "perl(Test::Memory::Cycle)")):
        amodule.register_command(list(chain(("dnf", "whatprovides"), order)),
                                 stdout=dnf_net_dns_output)
    amodule.register_command(("perl", "-V"), stdout=perl_V_output)
    for path in ("/No/Such/Module.pm", "/Test/Memory/Cycle.pm",
                 "/PadWalker.pm"):
        amodule.register_command(("apt-file", "search", path), rc=1)
    amodule.register_command(("apt-file", "search", "/WWW/Mechanize.pm"),
                             stdout=apt_search_www_mechanize_output)
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "No::Such::Module"), rc=1,
        stderr=cpanm_no_such_module_output)
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "Test::Memory::Cycle"),
        stdout=cpanm_test_memory_cycle_output)
    amodule.register_command(
        ("dnf", "whatprovides", "perl(PadWalker)"), rc=1,
        stdout=dnf_error_stdout, stderr=dnf_error_stderr)
    amodule.register_command(
        ("cpanm", "--local-lib-contained", "/not/a/real/directory",
         "--scandeps", "PadWalker"), stdout="""\
--> Working on PadWalker
Fetching http://www.cpan.org/authors/id/R/RO/ROBIN/PadWalker-2.5.tar.gz ... OK
Configuring PadWalker-2.5 ... OK
PadWalker-2.5
""")
    amodule.params = {
        "try_installed": True,
        "try_dnf": True,
        "try_apt": True,
        "try_cpanm": True,
    }
    result = {}
    errors = []
    missing = find_modules(
        amodule, result, errors, update=False,
        names=("No::Such::Module", "POSIX", "Net::DNS", "WWW::Mechanize",
               "Test::Memory::Cycle"))
    assert result["installed"] == set(("Devel::Cycle", "POSIX"))
    assert result["dnf"] == set(("perl(Net::DNS)",))
    assert result["apt"] == set(("libwww-mechanize-perl",))
    assert result["cpanm"] == set(("Test::Memory::Cycle", "PadWalker"))
    assert missing == set(("No::Such::Module",))
