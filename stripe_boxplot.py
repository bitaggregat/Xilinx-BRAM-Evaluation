from hdf5_wrapper.horrendous_copy_of_main import main, create_arg_parser


if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    arg_dict = vars(args)
    main(arg_dict)
