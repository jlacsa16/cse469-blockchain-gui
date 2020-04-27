import sys
import re
import os
import struct
from hashlib import sha1
from collections import namedtuple
from os import path
from datetime import datetime
from uuid import UUID

BLOCKCHAIN_PATH = os.getenv("BCHOC_FILE_PATH", default="blockchain.bin")
STATES = {
    "INITIAL": b"INITIAL\0\0\0\0",
    "CHECKEDIN": b"CHECKEDIN\0\0",
    "CHECKEDOUT": b"CHECKEDOUT\0",
    "DISPOSED": b"DISPOSED\0\0\0",
    "DESTROYED": b"DESTROYED\0\0",
    "RELEASED": b"RELEASED\0\0\0",
}
Block = namedtuple("Block", ["prev_hash", "timestamp", "case_id", "evidence_id", "state", "d_length", "data"])
BLOCK_FORMAT = "20s d 16s I 11s I"  # Format for byte padding in the struct
BLOCK_LEN = struct.calcsize(BLOCK_FORMAT)  # Length of a block. Should be 68
BLOCK_STRUCT = struct.Struct(BLOCK_FORMAT)  # Actual block struct


def main():
    if len(sys.argv) < 2:
        print_menu()
    else:
        if sys.argv[1] == "add":
            add()
        elif sys.argv[1] == "checkout":
            checkout()
        elif sys.argv[1] == "checkin":
            checkin()
        elif sys.argv[1] == "log":
            log()
        elif sys.argv[1] == "remove":
            remove()
        elif sys.argv[1] == "init":
            if len(sys.argv) > 2:
                sys.exit(1)
            else:
                init()
        elif sys.argv[1] == "verify":
            if len(sys.argv) > 2:
                sys.exit(1)
            else:
                verify()
        else:
            print_menu()


# add new evidence item to the blockchain, associate with case id (-c case)
# more than one item id may be given at a time (using -i), new state = "CHECKEDIN"
def add():
    # Parse cli arguments
    arguments = " ".join(sys.argv[1:])
    add_regex = r"((-i\s\w+)|(-c\s([^\s]+)))"
    add_args = re.findall(add_regex, arguments)
    case_id = None
    item_ids = []
    for match in add_args:
        if match[0][0:2] == "-c":
            if case_id is None:
                case_id = match[0][3:]
            else:  # Only allowed to have one case id
                sys.exit(1)
        elif match[0][0:2] == "-i":
            if match[0][3:0] not in item_ids:
                item_ids.append(int(match[0][3:]))
    # If no item_ids have been provided, case id is not a valid uuid-v4, exit
    if len(item_ids) < 1 or case_id is None:
        sys.exit(1)
    else:
        try:
            case_id = UUID(case_id, version=4)
        except ValueError:
            sys.exit(1)
    # Iterate of the blockchain to check if item ids already exist somewhere
    global BLOCKCHAIN_PATH
    last_block_hash = None
    if path.exists(BLOCKCHAIN_PATH):
        with open(BLOCKCHAIN_PATH, "rb") as blockchain:
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            while block_bytes:
                block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                block_data = blockchain.read(block[5])  # Get already unpacked data
                last_block_hash = sha1(block_bytes + block_data)
                if block[3] in item_ids:  # if item already exists, terminate
                    blockchain.close()
                    sys.exit(1)
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        blockchain.close()
    else:
        # Open a new blockchain file
        with open(BLOCKCHAIN_PATH, "wb") as blockchain:
            # Create a struct format
            initial_block = Block(
                prev_hash=0,
                timestamp=datetime.utcnow().timestamp(),
                case_id=UUID(int=0),
                evidence_id=0,
                state=STATES["INITIAL"],
                d_length=14,
                data=b"Initial block\0",
            )
            # Pack this struct into a padded binary block
            initial_block_packed = BLOCK_STRUCT.pack(
                initial_block.prev_hash.to_bytes(20, byteorder="little"),
                initial_block.timestamp,
                initial_block.case_id.int.to_bytes(16, byteorder="little"),
                initial_block.evidence_id,
                initial_block.state,
                len(initial_block.data),
            )
            last_block_hash = sha1(initial_block_packed + initial_block.data)
            # Write block and data separately
            blockchain.write(initial_block_packed)
            blockchain.write(initial_block.data)
            blockchain.close()
            print(
                "Blockchain file not found. Created INITIAL block.",
                "\nCase:",
                initial_block.case_id,
                "\nAdded item:",
                initial_block.evidence_id,
                "\n  Status:",
                initial_block.state.decode("utf-8").rstrip("\x00"),
                "\n  Time of action:",
                datetime.utcnow().isoformat() + "Z",
            )
    # Check for duplicate item ids
    with open(BLOCKCHAIN_PATH, "rb") as blockchain:
        block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        while block_bytes:
            block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
            blockchain.read(block[5])  # We done care b+out data so just skip it
            if block[3] in item_ids:
                sys.exit(1)
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
    blockchain.close()

    # Create new blocks from provided info
    if last_block_hash is not None:
        with open(BLOCKCHAIN_PATH, "ab") as blockchain:
            print("Case:", case_id)
            for item in item_ids:
                # Pack block to be saved, and write it
                block = Block(
                    prev_hash=last_block_hash.digest(),
                    timestamp=datetime.utcnow().timestamp(),
                    case_id=case_id,
                    evidence_id=int(item),
                    state=STATES["CHECKEDIN"],
                    d_length=0,
                    data=b"\0",
                )
                try:
                    packed_block = BLOCK_STRUCT.pack(
                        block.prev_hash,
                        block.timestamp,
                        block.case_id.int.to_bytes(16, byteorder="little"),
                        block.evidence_id,
                        block.state,
                        0,
                    )
                    blockchain.write(packed_block)
                    if block.d_length > 0:
                        blockchain.write(block.data)
                except Exception:
                    sys.exit(1)
                # Print obtained data
                print(
                    "Added item:",
                    item,
                    "\n  Status:",
                    STATES["CHECKEDIN"].decode("utf-8").rstrip("\x00"),
                    "\n  Time of action:",
                    datetime.utcnow().isoformat() + "Z",
                )
                # Save hash for next iteration
                last_block_hash = sha1(packed_block)
            blockchain.close()


# add new checkout entry, can only be performed on items already added to blockchain
def checkout():
    # Parse cli arguments
    arguments = " ".join(sys.argv[1:])
    checkout_regex = r"(-i\s\w+)"
    checkout_args = re.findall(checkout_regex, arguments)
    item_id = None
    if len(checkout_args) != 1:  # User must provide exactly one -i argument
        sys.exit(1)
    else:
        item_id = int(checkout_args[0][3:])
    # Read through the blockchain to find the last block with this item id
    last_found_block = None
    last_block_hash = None
    global BLOCKCHAIN_PATH
    if path.exists(BLOCKCHAIN_PATH):
        with open(BLOCKCHAIN_PATH, "rb") as blockchain:
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            while block_bytes:
                block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                block_data = blockchain.read(block[5])  # Get already unpacked data
                last_block_hash = sha1(block_bytes + block_data)
                if block[3] == item_id:  # if item already exists, terminate
                    last_found_block = block
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        blockchain.close()
    # if no blocks have been found, there's nothing to checkout
    if last_block_hash is None or last_found_block is None or last_found_block[4] != STATES["CHECKEDIN"]:
        sys.exit(1)
    else:
        # Create an updated block and write it
        block = Block(
            prev_hash=last_block_hash.digest(),
            timestamp=datetime.utcnow().timestamp(),
            case_id=UUID(int=int.from_bytes(last_found_block[2], byteorder="little")),
            evidence_id=last_found_block[3],
            state=STATES["CHECKEDOUT"],
            d_length=0,
            data=b"\0",
        )
        with open(BLOCKCHAIN_PATH, "ab") as blockchain:
            block_packed = BLOCK_STRUCT.pack(
                block.prev_hash,
                block.timestamp,
                block.case_id.int.to_bytes(16, byteorder="little"),
                block.evidence_id,
                block.state,
                block.d_length,
            )
            # Write block and data separately
            blockchain.write(block_packed)
            blockchain.close()
        print(
            "Case:",
            block.case_id,
            "\nAdded item:",
            block.evidence_id,
            "\n  Status:",
            block.state.decode("utf-8").rstrip("\x00"),
            "\n  Time:",
            datetime.fromtimestamp(block.timestamp).isoformat(),
        )


# add new checkin entry, can only be performed on item already added to the blockchain
# "-i" determines the item id to be checked in after it is added
def checkin():
    # Parse cli arguments to obtain id, or determine if the function call is invalid
    arguments = " ".join(sys.argv[1:])
    checkin_regex = r"(-i\s\w+)"
    checkin_args = re.findall(checkin_regex, arguments)
    item_id = None
    if len(checkin_args) != 1:  # User must provide exactly one -i argument
        sys.exit(1)
    else:
        item_id = int(checkin_args[0][3:])
    # Read through the blockchain to find the last block with this item id
    last_found_block = None
    last_block_hash = None
    global BLOCKCHAIN_PATH
    if path.exists(BLOCKCHAIN_PATH):
        with open(BLOCKCHAIN_PATH, "rb") as blockchain:
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            while block_bytes:
                block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                block_data = blockchain.read(block[5])  # Get already unpacked data
                last_block_hash = sha1(block_bytes + block_data)
                if block[3] == item_id:  # if item already exists, terminate
                    last_found_block = block
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        blockchain.close()
    # if no blocks have been found, there's nothing to checkout
    if last_block_hash is None or last_found_block is None or last_found_block[4] != STATES["CHECKEDOUT"]:
        sys.exit(1)
    else:
        # Create an updated block and write it
        block = Block(
            prev_hash=last_block_hash.digest(),
            timestamp=datetime.utcnow().timestamp(),
            case_id=UUID(int=int.from_bytes(last_found_block[2], byteorder="little")),
            evidence_id=last_found_block[3],
            state=STATES["CHECKEDIN"],
            d_length=0,
            data=b"\0",
        )
        with open(BLOCKCHAIN_PATH, "ab") as blockchain:
            block_packed = BLOCK_STRUCT.pack(
                block.prev_hash,
                block.timestamp,
                block.case_id.int.to_bytes(16, byteorder="little"),
                block.evidence_id,
                block.state,
                block.d_length,
            )
            # Write block and data separately
            blockchain.write(block_packed)
            blockchain.close()
        print(
            "Case:",
            block.case_id,
            "\nAdded item:",
            block.evidence_id,
            "\n  Status:",
            block.state.decode("utf-8").rstrip("\x00"),
            "\n  Time of action:",
            datetime.fromtimestamp(block.timestamp).isoformat(),
        )


# Display blockchain oldest to newest (unless -r is given for reverse)
def log():
    # Parse cli arguments
    arguments = " ".join(sys.argv[1:])
    log_regex = r"((-i|-n)\s\w+|-r|--reverse|(-c\s([^\s]+)))"
    log_args = re.finditer(log_regex, arguments)
    reverse = False
    number_of_items = 0
    case_ids = []
    item_ids = []
    for match in log_args:
        groups = match.groups()
        if groups[0] == "-r" or groups[0] == "--reverse":
            reverse = True
        elif groups[1] == "-n":
            number_of_items = int(groups[0][3:])
        elif groups[0][0:2] == "-c":
            if groups[3] not in case_ids:
                try:
                    case_ids.append(UUID(groups[3], version=4))
                except Exception:
                    sys.exit(1)
        elif groups[1] == "-i":
            if groups[0][3:] not in item_ids:
                item_ids.append(int(groups[0][3:]))
    # Obtain blocks for later analysis
    all_blocks = []
    global BLOCKCHAIN_PATH
    if path.exists(BLOCKCHAIN_PATH):
        with open(BLOCKCHAIN_PATH, "rb") as blockchain:
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            while block_bytes:
                block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                if (
                    (len(case_ids) == 0 and len(item_ids) == 0 and block not in all_blocks)
                    or (len(case_ids) == 0 and block[3] in item_ids and block not in all_blocks)
                    or (
                        len(item_ids) == 0
                        and UUID(int=int.from_bytes(block[2], byteorder="little")) in case_ids
                        and block not in all_blocks
                    )
                    or (
                        block[3] in item_ids
                        and UUID(int=int.from_bytes(block[2], byteorder="little")) in case_ids
                        and block not in all_blocks
                    )
                ):
                    all_blocks.append(block)
                blockchain.read(block[5])  # We done care b+out data so just skip it
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        blockchain.close()
    else:
        # Open a new blockchain file
        blockchain = open(BLOCKCHAIN_PATH, "ab")
        # Create a struct format
        initial_block = Block(
            prev_hash=0,
            timestamp=datetime.utcnow().timestamp(),
            case_id=UUID(int=0),
            evidence_id=0,
            state=STATES["INITIAL"],
            d_length=14,
            data=b"Initial block\0",
        )
        all_blocks.append(initial_block)
        # Pack this struct into a padded binary block
        initial_block_packed = BLOCK_STRUCT.pack(
            initial_block.prev_hash.to_bytes(20, byteorder="little"),
            initial_block.timestamp,
            initial_block.case_id.int.to_bytes(16, byteorder="little"),
            initial_block.evidence_id,
            initial_block.state,
            len(initial_block.data),
        )
        # Write block and data separately
        blockchain.write(initial_block_packed)
        blockchain.write(initial_block.data)
        blockchain.close()
        print("Blockchain file not found. Created INITIAL block.")
    # If -n param was not given, determine the max amount
    if number_of_items == 0:
        number_of_items = len(all_blocks)
    # Print out results according to provided params
    if len(all_blocks) > 0:
        if reverse:
            for block in reversed(all_blocks):
                if number_of_items == 0:
                    break
                else:
                    print("Case:", UUID(int=int.from_bytes(block[2], byteorder="little")))
                    print("Item:", block[3])
                    print("Action:", block[4].decode("utf-8").rstrip("\x00"))
                    print("Time:", datetime.fromtimestamp(block[1]).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
                    number_of_items -= 1
                    if number_of_items != 0:
                        print()
        else:
            for block in all_blocks:
                if number_of_items == 0:
                    break
                else:
                    print("Case:", UUID(int=int.from_bytes(block[2], byteorder="little")))
                    print("Item:", block[3])
                    print("Action:", block[4].decode("utf-8").rstrip("\x00"))
                    print("Time:", datetime.fromtimestamp(block[1]).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
                    number_of_items -= 1
                    if number_of_items != 0:
                        print()


# prevent further action on a given evidence, item must be "CHECKEDIN"
# changes the tag of the evidence to "RELEASED", "DESTROYED", or "DISPOSED"
def remove():
    # Find -o params and fix the quote encapsulated string
    # Shell removes the quotes when parsing arguments, but keeps the whole string as a single param
    # for index, argument in enumerate(sys.argv):
    #    if argument == "-o":
    #        sys.argv[index + 1] = '"%s"' % (sys.argv[index + 1])

    # Parse params
    arguments = " ".join(sys.argv[1:])
    # remove_regex = r"((-i|-y|--why)\s\w+|(-o\s\"(.*?)\"))"
    remove_regex = r"((-i|-y|--why)\s\w+|(-o\s(.*\w+)))"
    remove_args = re.finditer(remove_regex, arguments)
    item_id = None
    reason = None
    owner = None
    for match in remove_args:
        groups = match.groups()
        if groups[1] == "-i":
            if item_id is None:
                item_id = int(groups[0][3:])
            else:
                sys.exit(1)
        elif groups[1] == "-y":
            if reason is None:
                reason = groups[0][3:]
            else:
                sys.exit(1)
        elif groups[1] == "--why":
            if reason is None:
                reason = groups[0][6:]
        elif groups[0][0:2] == "-o" and owner is None:
            owner = groups[3]
    # Group index needs to be fixed because it can contain parts of another param
    if owner is not None:
        possible_indexes = []
        try:
            possible_indexes.append(owner.index("-y"))
        except ValueError:
            pass
        try:
            possible_indexes.append(owner.index("--why"))
        except ValueError:
            pass
        try:
            possible_indexes.append(owner.index("-i"))
        except ValueError:
            pass
        if len(possible_indexes) > 0:
            owner = owner[0 : min(possible_indexes)]  # noqa: E203
    # This needs a list of item ids, and a reason
    # Reason format must be one of the three
    # If reason is RELEASED, owned must be specified
    if (
        (item_id is None or reason is None)
        or (reason != "DISPOSED" and reason != "DESTROYED" and reason != "RELEASED")
        or (reason == "RELEASED" and owner is None)
    ):
        sys.exit(1)
    last_found_block = None
    last_block_hash = None
    global BLOCKCHAIN_PATH
    if path.exists(BLOCKCHAIN_PATH):
        with open(BLOCKCHAIN_PATH, "rb") as blockchain:
            block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            while block_bytes:
                block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                block_data = blockchain.read(block[5])  # Get already unpacked data
                last_block_hash = sha1(block_bytes + block_data)
                if block[3] == item_id:  # if item already exists, terminate
                    last_found_block = block
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
        blockchain.close()
    # if no blocks have been found, there's nothing to checkout
    if last_block_hash is None or last_found_block is None or last_found_block[4] != STATES["CHECKEDIN"]:
        sys.exit(1)
    else:
        # Create an updated block and write it
        data_length = 0
        original_owner = None
        if owner is None:
            original_owner = ""
            owner = b"\0"
        else:
            original_owner = owner
            owner = owner + "\0"
            data_length = len(owner)
        block = Block(
            prev_hash=last_block_hash.digest(),
            timestamp=datetime.utcnow().timestamp(),
            case_id=UUID(int=int.from_bytes(last_found_block[2], byteorder="little")),
            evidence_id=last_found_block[3],
            state=STATES[reason],
            d_length=data_length,
            data=owner,
        )
        with open(BLOCKCHAIN_PATH, "ab") as blockchain:
            block_packed = BLOCK_STRUCT.pack(
                block.prev_hash,
                block.timestamp,
                block.case_id.int.to_bytes(16, byteorder="little"),
                block.evidence_id,
                block.state,
                block.d_length,
            )
            # Write block and data separately
            blockchain.write(block_packed)
            if data_length > 0:
                blockchain.write(owner.encode("utf-8"))
            blockchain.close()
        print(
            "Case:",
            block.case_id,
            "\nRemoved item:",
            block.evidence_id,
            "\n  Status:",
            block.state.decode("utf-8").rstrip("\x00"),
            "\n  Owner info:",
            original_owner,
            "\n  Time of action:",
            datetime.fromtimestamp(block.timestamp),
        )


# starts up or checks for initial block
def init():
    global BLOCKCHAIN_PATH
    if path.exists(BLOCKCHAIN_PATH):
        try:
            blockchain = open(BLOCKCHAIN_PATH, "rb")
            initial_block = BLOCK_STRUCT.unpack(blockchain.read(BLOCK_LEN))
            blockchain.close()
            if initial_block[4] == STATES["INITIAL"]:
                print("Blockchain file found with INITIAL block.")
            else:
                sys.exit(1)
        except Exception:
            sys.exit(1)
    else:
        # Open a new blockchain file
        blockchain = open(BLOCKCHAIN_PATH, "ab")
        # Create a struct format
        initial_block = Block(
            prev_hash=0,
            timestamp=datetime.utcnow().timestamp(),
            case_id=UUID(int=0),
            evidence_id=0,
            state=STATES["INITIAL"],
            d_length=14,
            data=b"Initial block\0",
        )
        # Pack this struct into a padded binary block
        initial_block_packed = BLOCK_STRUCT.pack(
            initial_block.prev_hash.to_bytes(20, byteorder="little"),
            initial_block.timestamp,
            initial_block.case_id.int.to_bytes(16, byteorder="little"),
            initial_block.evidence_id,
            initial_block.state,
            len(initial_block.data),
        )
        # Write block and data separately
        blockchain.write(initial_block_packed)
        blockchain.write(initial_block.data)
        blockchain.close()
        print("Blockchain file not found. Created INITIAL block.")


# parse blockchain and validate all entries
def verify():
    # Iterate of the blockchain to check if item ids already exist somewhere
    global BLOCKCHAIN_PATH
    all_previous_hashes = []
    all_hashes = []
    evidence_states = {}
    if path.exists(BLOCKCHAIN_PATH):
        try:
            with open(BLOCKCHAIN_PATH, "rb") as blockchain:
                block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
                while block_bytes:
                    block = BLOCK_STRUCT.unpack(block_bytes)  # Unpack the block itself
                    block_data = blockchain.read(block[5])  # Get already unpacked data
                    all_previous_hashes.append(block[0].hex())  # Obtain previous_hash from every block in the chain
                    all_hashes.append(sha1(block_bytes + block_data).hexdigest())  # Obtain hash of current block
                    # Check if evidence state is wrong
                    try:
                        if (  # If an item has been removed, it cannot appear again
                            evidence_states[block[3]] == STATES["DISPOSED"]
                            or evidence_states[block[3]] == STATES["RELEASED"]
                            or evidence_states[block[3]] == STATES["DESTROYED"]
                        ):
                            if block[4] in STATES.values():
                                sys.exit(1)
                        elif (  # no double checkouts
                            evidence_states[block[3]] == STATES["CHECKEDOUT"] and evidence_states[block[3]] == block[4]
                        ) or (  # no double checkins
                            evidence_states[block[3]] == STATES["CHECKEDIN"] and evidence_states[block[3]] == block[4]
                        ):
                            sys.exit(1)
                        elif block[4] not in STATES.values():  # some kind of a fake state
                            sys.exit(1)
                    except KeyError:
                        pass
                    # Record last known evidence item state
                    evidence_states[block[3]] = block[4]
                    # Check owner status in case block was RELEASED
                    if block[4] == STATES["RELEASED"]:
                        if block[5] == 0:
                            sys.exit(1)
                    # Continue reading
                    block_bytes = blockchain.read(BLOCK_LEN)  # Parse the block
            blockchain.close()
        except struct.error:
            sys.exit(1)
        print("Transactions in blockchain:", len(all_hashes))
        # Check for blocks with missing parent
        for i, hash in enumerate(all_previous_hashes):
            if i != 0 and hash not in all_hashes:
                print("State of blockchain: ERROR", "\nBad block:", all_hashes[i], "\nParent block: NOT FOUND")
                sys.exit(1)

        # Check if there any blocks with the same parent
        prev_hash_duplicate_check = set([x for x in all_previous_hashes if all_previous_hashes.count(x) > 1])
        if len(prev_hash_duplicate_check) > 0:
            try:
                t = list(prev_hash_duplicate_check)[0]
                index = None
                for i, hash in enumerate(all_previous_hashes):
                    if hash == t:
                        index = i
                if index is not None:
                    print(
                        "State of blockchain: ERROR",
                        "\nBad block:",
                        all_hashes[index],
                        "\nParent block:",
                        all_previous_hashes[index],
                        "\nTwo blocks found with same parent.",
                    )
                    sys.exit(1)
            except ValueError:
                pass
        print("State of blockchain: CLEAN")
    else:
        print("Transactions in blockchain: 0")


def print_menu():
    print(
        "bchoc [param]\n"
        "Parameters:\n"
        "\tadd -c case_id -i item_id [-i item_id ...]\n"
        "\tcheckout -i item_id\n"
        "\tcheckin -i item_id\n"
        "\tlog [-r] [-n num_entries] [-c case_id] [-i item_id]\n"
        "\tremove -i item_id -y reason [-o owner]\n"
        "\tinit\n"
        "\tverify\n"
        "Tags:\n"
        "\t-c case_id\tMust be a valid UUID. When used with log only blocks with the given case_id are returned.\n"
        "\t-i item_id\tWhen used with log only blocks with the given item_id are returned. "
        "The item ID must be unique within the blockchain.\n"
        "\t-r, --reverse\tReverses the order of the block entries to show the most recent entries first.\n"
        "\t-n num_entries\tWhen used with log, shows num_entries number of block entries.\n"
        "\t-y reason, --why reason\tMust be one of: DISPOSED, DESTROYED, or RELEASED. If the reason given is RELEASED,"
        "-o must also be given.\n"
        "\t-o owner\tInformation about the lawful owner to whom the evidence was released\n"
    )


main()
