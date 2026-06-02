from __future__ import annotations

import argparse

from app import analytics, storage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASCII 风格人脸识别签到系统")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="注册用户人脸")
    register.add_argument("--user-id", required=True)
    register.add_argument("--name", required=True)
    register.add_argument("--image", required=True)

    subparsers.add_parser("run", help="启动签到流程")
    subparsers.add_parser("stats", help="查看签到统计")

    serve = subparsers.add_parser("serve", help="启动前端交互 API 服务")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    demo = subparsers.add_parser("demo-checkin", help="写入一条演示签到记录")
    demo.add_argument("--user-id", default="2026001")
    demo.add_argument("--name", default="测试学生")
    return parser


def handle_register(args) -> None:
    from app import face_recognize

    face_recognize.register_face(args.user_id, args.name, args.image)
    print(f"注册成功: {args.name} ({args.user_id})")


def handle_stats() -> None:
    summary = analytics.summarize_attendance()
    print("签到统计")
    print(summary)


def handle_demo_checkin(args) -> None:
    from app import attendance

    record = attendance.mark_attendance(args.user_id, args.name)
    print("演示签到结果")
    print(record)


def handle_serve(args) -> None:
    from app import api_server

    api_server.run_server(args.host, args.port)


def handle_run() -> None:
    import cv2

    from app import ascii_render, attendance, camera, config, face_detect, face_recognize, preprocess

    known_faces = face_recognize.load_known_faces()
    capture = camera.open_camera()
    print("按 Ctrl+C 退出签到流程。")

    try:
        while True:
            success, frame = capture.read()
            if not success:
                print("读取摄像头帧失败")
                break

            gray_frame = preprocess.prepare_frame(frame, config.FRAME_SCALE)
            locations = face_detect.locate_faces(gray_frame)
            matches = face_recognize.match_faces(
                gray_frame,
                locations,
                known_faces,
                config.LBPH_CONFIDENCE_THRESHOLD,
            )

            status_text = "No face"
            for match in matches:
                if match["matched"]:
                    record = attendance.mark_attendance(match["user_id"], match["name"])
                    status_text = f'{match["name"]}: {record["status"]}'
                else:
                    status_text = "Unknown user"

            ascii_output = ascii_render.frame_to_ascii(frame, config.ASCII_WIDTH, config.ASCII_CHARS)
            print("\033[2J\033[H", end="")
            print(ascii_output)
            print()
            print(f"Status: {status_text}")

            cv2.waitKey(1)
    except KeyboardInterrupt:
        print("\n签到流程已退出。")
    finally:
        capture.release()


def main() -> None:
    storage.ensure_data_dirs()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "register":
        handle_register(args)
    elif args.command == "run":
        handle_run()
    elif args.command == "stats":
        handle_stats()
    elif args.command == "serve":
        handle_serve(args)
    elif args.command == "demo-checkin":
        handle_demo_checkin(args)


if __name__ == "__main__":
    main()
